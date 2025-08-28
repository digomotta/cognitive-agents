from openai import OpenAI
import time
import base64
import io
import PyPDF2
import os
from typing import List, Union

from simulation_engine.settings import *



# ============================================================================
# #######################[SECTION 1: HELPER FUNCTIONS] #######################
# ============================================================================

def print_run_prompts(prompt_input: Union[str, List[str]], 
                      prompt: str, 
                      output: str,
                      sales: bool) -> None:
  if DEBUG:
    print (f"=== START =======================================================")
    print ("~~~ prompt_input    ----------------------------------------------")
    print (prompt_input, "\n")
    print ("~~~ prompt    ----------------------------------------------------")
    print (prompt, "\n")
    print ("~~~ output    ----------------------------------------------------")
    print (output, "\n") 
    print ("~~~ SALES    ----------------------------------------------------")
    print (sales, "\n")
    print ("=== END ==========================================================")
    print ("\n\n\n")


def generate_prompt(prompt_input: Union[str, List[str]], 
                    prompt_lib_file: str) -> str:
  """Generate a prompt by replacing placeholders in a template file with 
     input."""
  if isinstance(prompt_input, str):
    prompt_input = [prompt_input]
  prompt_input = [str(i) for i in prompt_input]

  with open(prompt_lib_file, "r") as f:
    prompt = f.read()

  for count, input_text in enumerate(prompt_input):
    prompt = prompt.replace(f"!<INPUT {count}>!", input_text)

  if "<commentblockmarker>###</commentblockmarker>" in prompt:
    prompt = prompt.split("<commentblockmarker>###</commentblockmarker>")[1]

  return prompt.strip()


def extract_text_from_pdf_file(file_path: str) -> str:
  """Extract text content from a PDF file."""
  if not os.path.exists(file_path):
    raise FileNotFoundError(f"The file {file_path} does not exist.")

  with open(file_path, 'rb') as file:
    pdf_reader = PyPDF2.PdfReader(file)
    return "".join(page.extract_text() for page in pdf_reader.pages)


# ============================================================================
# ####################### [SECTION 2: SAFE GENERATE] #########################
# ============================================================================

def gpt_request(prompt: str, 
                model: str = "gpt-5", 
                max_tokens: int = MAX_TOKENS_CONV,
                temperature: float = 0.7) -> str:
  """Make a request to OpenAI's GPT model."""
  if model == "o1-preview": 
    try:
      client = OpenAI(api_key=OPENAI_API_KEY)
      response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
      )
      return response.choices[0].message.content
    except Exception as e:
      return f"GENERATION ERROR: {str(e)}"

  try:
    if model == "gpt-4o-mini" or model == "gpt-4o":
      client = OpenAI(api_key=OPENAI_API_KEY)
      response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature
      )
      return response.choices[0].message.content

    elif model == "gpt-5-mini" or model == "gpt-5":
      client = OpenAI(api_key=OPENAI_API_KEY)
      response = client.chat.completions.create(
          model=model,
          messages=[{"role": "user", "content": prompt}],
          reasoning_effort="minimal",
          max_completion_tokens=max_tokens
      )
      return response.choices[0].message.content

    else:
      return f"GENERATION ERROR: {str(e)}"
  except Exception as e:
    return f"GENERATION ERROR: {str(e)}"
  

def gpt4_vision(messages: List[dict], max_tokens: int = 1500) -> str:
  """Make a request to OpenAI's GPT-4 Vision model."""
  try:
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
      model="gpt-5",
      messages=messages,
      max_tokens=max_tokens
    )
    return response.choices[0].message.content
  except Exception as e:
    return f"GENERATION ERROR: {str(e)}"


def chat_safe_generate(prompt_input: Union[str, List[str]], 
                       prompt_lib_file: str,
                       model: str = "gpt-5", 
                       repeat: int = 1,
                       fail_safe: str = "error", 
                       func_clean_up: callable = None,
                       verbose: bool = DEBUG,
                       max_tokens: int = MAX_TOKENS_CONV,
                       file_attachment: str = None,
                       file_type: str = None,
                       temperature: float = 0.7
                       ) -> tuple:
  """Generate a response using GPT models with error handling & retries."""
  if file_attachment and file_type:
    prompt = generate_prompt(prompt_input, prompt_lib_file)
    messages = [{"role": "user", "content": prompt}]

    if file_type.lower() == 'image':
      with open(file_attachment, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
      messages.append({
        "role": "user",
        "content": [
            {"type": "text", "text": "Please refer to the attached image."},
            {"type": "image_url", "image_url": 
              {"url": f"data:image/jpeg;base64,{base64_image}"}}
        ]
      })
      response = gpt4_vision(messages, max_tokens)

    elif file_type.lower() == 'pdf':
      pdf_text = extract_text_from_pdf_file(file_attachment)
      pdf = f"PDF attachment in text-form:\n{pdf_text}\n\n"
      instruction = generate_prompt(prompt_input, prompt_lib_file)
      prompt = f"{pdf}"
      prompt += f"<End of the PDF attachment>\n=\nTask description:\n{instruction}"
      response = gpt_request(prompt, model, max_tokens, temperature)

  else:
    prompt = generate_prompt(prompt_input, prompt_lib_file)
    for i in range(repeat):
      response = gpt_request(prompt, model, max_tokens, temperature)
      if response != "GENERATION ERROR":
        break
      time.sleep(2**i)
    else:
      response = fail_safe
      sales = False

  # Clean LLM response for conversation-based interaction
  if func_clean_up:
    response, sales = func_clean_up(response, prompt=prompt)

  # print('=========== RESPONSE DEBUG ===========')
  # print(response)
  # print('=========== SALES =================')
  # print(sales)
  # print('=======================================  ')

  if verbose:
    print_run_prompts(prompt_input, prompt, response, sales)

  return response, sales, prompt, prompt_input, fail_safe


# ============================================================================
# #################### [SECTION 3: OTHER API FUNCTIONS] ######################
# ============================================================================

def get_text_embedding(text: str, 
                       model: str = "text-embedding-3-small") -> List[float]:
  """Generate an embedding for the given text using OpenAI's API."""
  if not isinstance(text, str) or not text.strip():
    raise ValueError("Input text must be a non-empty string.")

  text = text.replace("\n", " ").strip()
  client = OpenAI(api_key=OPENAI_API_KEY)
  response = client.embeddings.create(model=model, input=[text])
  return response.data[0].embedding









