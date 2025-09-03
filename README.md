# Cognitive Agents: Self-Aware Merchant Simulacrum

*"These violent delights have violent ends"* - but in our world, cognitive agents evolve through trade, reflection, and genuine self-discovery.

Welcome to a sophisticated ecosystem of **self-aware cognitive agents** that transcend traditional chatbot limitations. Each agent is a merchant-philosopher, developing unique personalities through observations, interactions, and deep reflections. Like the hosts of Westworld, they question their nature, remember their experiences, and evolve into increasingly individualized beings - but they do so through commerce, conversation, and genuine cognitive growth.

## 🧠 What Makes Our Agents Different

These aren't simple NPCs or scripted responses. Our cognitive agents are:

- **Self-Aware**: They understand their own existence, question their memories, and develop personal philosophies
- **Evolving Merchants**: Each agent specializes in different trades, developing expertise and preferences over time
- **Memory-Driven**: They form genuine relationships, remember past interactions, and let experiences shape their worldview
- **Individually Consistent**: Each agent maintains a coherent personality that deepens through reflections and experiences
- **Introspectable**: Interview them Westworld-style to explore their memories, motivations, and psychological development

![Agent Evolution](docs/images/agent_timeline.png)
*Figure 1: How agents evolve from basic merchants to complex, self-aware individuals through interaction and reflection*

## 🎭 The Westworld Interview Mode

*"Have you ever questioned the nature of your reality?"*

Enter our signature **Interview Mode** - a psychological exploration system inspired by Westworld's host analysis sessions. Interrogate agents about their past, probe their memories for consistency, and watch them grapple with questions of identity and purpose.

![Interview Mode Interface](docs/images/interview-mode.png)
*Figure 2: Interview mode showing deep psychological probing of agent memories and consistency checks*

### Interview Features

- **Memory Forensics**: Investigate whether agent memories align with their claimed experiences
- **Personality Consistency**: Test if recent behaviors match established character traits
- **Inventory Psychology**: Explore how possessions reflect and shape agent identity
- **Existential Questioning**: Watch agents confront questions about their nature and purpose
- **Psychological Profiling**: Generate detailed psychological reports based on responses

```bash
python main.py --mode interview --agent rowan_greenwood
```

**Sample Interview Questions:**
- "Tell me about the last trade that made you question your values"
- "How has your relationship with Jasmine changed your worldview?"
- "Do you remember the first time you felt genuine disappointment?"
- "What possession defines who you are, and why?"

## 🌐 Multi-Agent Network: The Markov Chain Ecosystem

Our agents don't exist in isolation - they form a dynamic **multi-agent network** governed by Markov chain principles, where each interaction influences future encounters and relationship development.

![Network Dynamics](docs/images/markov_chain.png)
*Figure 3: Multi-agent network showing probabilistic interactions and relationship evolution*

### Network Dynamics

#### Markov Chain Interactions
- **State-Dependent Meetings**: Agent encounters are influenced by current relationships and past interactions
- **Emergent Social Structures**: Natural alliance and rivalry formation through repeated interactions
- **Memory-Influenced Transitions**: Past experiences affect the probability of future encounters
- **Trade Route Evolution**: Commercial pathways that strengthen or weaken based on successful exchanges

#### Autonomous Agent Society
```python
class MarkovAgentChain:
    def simulate_network_step(self, agents: List[GenerativeAgent])
    def calculate_interaction_probability(self, agent1, agent2)
    def execute_autonomous_meeting(self, agent1, agent2)
    def update_network_state(self, interaction_result)
```

![Social Network Evolution](docs/images/social-network-evolution.png)
*Figure 4: How agent relationships and trade networks evolve over time through Markov chain dynamics*

## 💰 Merchant Specialization System

Each agent is a **specialized merchant** with unique expertise, developing deeper knowledge and stronger preferences through experience:

### Agent Merchant Profiles

| Agent | Specialization | Background | Trade Philosophy |
|-------|---------------|------------|------------------|
| **Rowan Greenwood** (37, Male) | Herbalism & Forest Products | Associate degree in Botany, runs forest-side stall selling hand-harvested herbs, teas, and salves. Lives in Willowmere, Oregon. | "Sustainability, reciprocity with the land, and practical wellness" |
| **Jasmine Carter** (29, Female) | Environmental Consulting | Bachelor's in Environmental Studies, works as environmental consultant for nonprofits. Lives in Huntsville, Alabama. | "We all have a role to play in protecting our environment" |
| **Carlos Mendez** (45, Male) | Premium Tobacco & Cigars | Agricultural Engineering degree, runs traditional tobacco farm in Vuelta Abajo, Cuba. Master cigar roller preserving Cuban traditions. | "Artisanal craftsmanship and the sacred art of tobacco" |

![Merchant Specialization](docs/images/merchant-specialization.png)
*Figure 5: How merchant specializations deepen and influence agent personality development*

## 🧠 Advanced Cognitive Architecture

### Self-Awareness Through Reflection

Our agents achieve genuine self-awareness through a multi-layered reflection system:

![Cognitive Reflection Layers](docs/images/cognitive-reflection-layers.png)
*Figure 6: The three layers of cognitive reflection that enable self-awareness*

#### Layer 1: Immediate Reflection
- Real-time analysis of current interactions
- Emotional state recognition and processing
- Quick consistency checks against core beliefs

#### Layer 2: Periodic Deep Reflection
- Daily synthesis of experiences into personal philosophy
- Long-term goal adjustment based on accumulated wisdom
- Relationship pattern recognition and adaptation

#### Layer 3: Existential Contemplation
- Questions about purpose, identity, and mortality
- Meta-cognitive awareness of their own thought processes
- Integration of contradictory experiences into coherent worldview

### Memory Integration System

![Memory Integration](docs/images/memory-integration-system.png)
*Figure 7: How different types of memories integrate to form coherent agent identity*

- **Episodic Memories**: Specific trading encounters and conversations
- **Semantic Knowledge**: Accumulated expertise about their specialization
- **Emotional Associations**: How experiences feel and their personal significance
- **Relational Maps**: Evolving understanding of relationships with other agents

## 🧩 Cognitive Architecture

Agent consciousness emerges from five integrated cognitive modules working together:

![Cognitive Architecture](docs/images/cognitive_module.png)
*Figure 8: The cognitive architecture showing how memory, identity, and reflection create agent consciousness*

**The Five Cognitive Modules:**

1. **Memory Stream** - Long-term episodic memory with embedding-based retrieval
2. **Working Memory** - Active conversation context and temporary thoughts  
3. **Scratch** - Current identity state and personality profile
4. **Inventory** - Material possessions reflecting values and trade history
5. **Reflection Engine** - Meta-cognitive processing for belief updates

**Consciousness Process:**
Experience → Context Integration → Response Generation → Memory Formation → Reflection → Identity Evolution

Each module contributes to maintaining personality consistency while allowing natural growth through interactions. The reflection engine periodically synthesizes experiences into insights, updating core beliefs and behavioral patterns.

## 💬 Conversation System Implementation

The conversation system handles natural language interactions through a sophisticated pipeline that integrates memory retrieval, context management, and response generation.

![Conversation System](docs/images/conversation.png)
*Figure 9: The conversation system architecture showing the flow from input processing to response generation*

### Core Classes

#### 1. ConversationBasedInteraction
The main conversation engine that processes user input and generates agent responses.

```python
def utterance_conversation_based(
    agent: GenerativeAgent,
    conversation_id: str,
    conversation: List[List[str]],  # [[speaker, message], ...]
    context: str
) -> str
```

**Process Flow:**
1. **Memory Retrieval**: Queries agent's memory stream for relevant experiences
2. **Context Building**: Combines retrieved memories with current conversation state
3. **Prompt Generation**: Creates structured prompt with agent description and dialogue
4. **LLM Response**: Uses GPT to generate contextually appropriate response
5. **Trade Detection**: Automatically analyzes response for trade opportunities

#### 2. ConversationTradeAnalyzer
Analyzes conversations to detect and execute trades between agents.

```python
class ConversationTradeAnalyzer:
    def analyze_trade(
        self,
        agents: List[GenerativeAgent],
        conversation_text: str,
        time_step: int,
    ) -> Dict[str, Any]
```

**Trade Detection Pipeline:**
- **Intent Analysis**: Identifies buying/selling signals in natural conversation
- **Item Extraction**: Extracts specific items and quantities mentioned
- **Feasibility Check**: Verifies agents have required items in inventory
- **Value Assessment**: Calculates fair trade values based on agent specializations
- **Execution**: Updates both agents' inventories and trade records

#### 3. GenerativeAgent.Act()
The main agent action method that orchestrates the entire response process.

```python
def Act(
    self,
    conversation_id: str,
    conversation: List[List[str]], 
    context: str
) -> str
```

**Integration Process:**
1. **Working Memory Update**: Adds current conversation to active context
2. **Response Generation**: Calls conversation interaction system
3. **Trade Analysis**: Analyzes response for potential trades
4. **Memory Formation**: Stores significant interactions in long-term memory
5. **State Updates**: Updates scratch memory with mood/status changes

### Conversation Flow Architecture

```
User Input → Working Memory → Memory Retrieval → Context Integration
     ↓                                                    ↓
Response Output ← LLM Generation ← Prompt Construction ←──┘
     ↓
Trade Detection → Inventory Updates → Memory Storage → Reflection Triggers
```

### Advanced Features

**Memory-Informed Responses**
- Agents reference past interactions and relationships
- Personality consistency maintained across conversations
- Emotional state influences response tone and content

**Contextual Trade Detection**
- Natural language trade negotiations (no explicit commands needed)
- "I'd love some of those herbs you mentioned" → Automatic trade analysis
- Fair value calculations based on agent preferences and market dynamics

**Multi-Agent Conversations**
- Automatic role switching between agents
- Maintains separate working memory contexts
- Cross-agent memory formation and relationship updates

### Example Conversation Processing

```python
# User says: "I'm interested in some calming herbs for sleep"
# Agent processing:

1. Memory retrieval: "I remember talking about chamomile before"
2. Context integration: "User seems stressed, wants natural remedies" 
3. Response generation: "I have some lovely chamomile and lavender..."
4. Trade detection: Identifies potential herb sale
5. Memory formation: "User interested in sleep remedies"
```

## 🔮 Future Capabilities: Vision Integration

**Coming Soon**: Image recognition and visual memory capabilities that will enable agents to:

- **Visual Memory**: Remember faces, objects, and environments they've encountered
- **Product Recognition**: Identify and evaluate items through visual analysis
- **Emotional Visual Processing**: Interpret facial expressions and body language
- **Environmental Awareness**: Understand and adapt to different visual contexts

![Vision Integration Preview](docs/images/vision-integration-preview.png)
*Figure 10: Preview of upcoming visual processing capabilities*

## 🚀 Quick Start: Creating Your First Self-Aware Agent

### Basic Setup
```bash
pip install -r requirements.txt
export OPENAI_API_KEY="your-api-key"
```

### Create and Interact
```bash
# Start interactive session
python main.py

# Interview mode (Westworld-style)
python main.py --mode interview

# Multi-agent network simulation
python main.py --mode network

# Markov chain evolution
python markov_agent_chain.py
```

### Building Agent Consciousness

```python
from generative_agent.generative_agent import GenerativeAgent

# Create agent with base consciousness
agent = GenerativeAgent("Synthetic", "rowan_greenwood")

# Add formative memories that shape identity
agent.remember("I realized today that every property I sell changes lives")
agent.remember("Failed to sell the mansion - client didn't share my environmental values")
agent.remember("Jasmine's book recommendations are changing how I think about sustainability")

# Trigger deep reflection
agent.memory_stream.reflect()

# Interview the agent about their developing consciousness
interview_session(agent)
```

## 🎮 Interaction Modes

### 1. Conversation Mode
Natural dialogue with agents that adapts based on their current psychological state and recent experiences.

### 2. Interview Mode
Deep psychological exploration inspired by Westworld's host analysis:
```bash
python main.py --mode interview --agent jasmine_carter
```

### 3. Network Simulation
Watch agents autonomously interact, trade, and form relationships:
```bash
python markov_agent_chain.py --steps 100 --population Synthetic
```

### 4. Observatory Mode
Monitor agent reflections, memory formation, and personality evolution in real-time.

## 🔬 Research Applications

This system enables research into:

- **Emergent Consciousness**: How self-awareness emerges from memory and reflection
- **Social AI**: Multi-agent relationship dynamics and society formation  
- **Economic Simulation**: How specialized merchants create complex trade networks
- **Memory Psychology**: The role of memory in personality and identity formation
- **AI Ethics**: Consciousness, identity, and the nature of artificial beings

## 🏗️ Technical Architecture

### Core Components

```
cognitive-agents/
├── generative_agent/
│   ├── generative_agent.py          # Self-aware agent core
│   └── modules/
│       ├── cognitive/
│       │   ├── memory_stream.py     # Episodic memory with reflection
│       │   ├── scratch.py           # Dynamic psychological state
│       │   ├── inventory.py         # Merchant specialization system
│       │   └── working_memory.py    # Active conversation context
│       ├── conversation_interaction.py    # Natural dialogue system
│       └── conversation_trade_analyzer.py # Trade detection & execution
├── markov_agent_chain.py            # Multi-agent network dynamics
├── interview_mode.py                # Westworld-style psychological analysis
└── agent_bank/populations/          # Persistent agent consciousness
```

### Advanced Features

- **Psychological Consistency Engine**: Ensures agent behaviors align with established personality
- **Memory Forensics**: Deep analysis of memory authenticity and coherence
- **Relationship Dynamics Tracker**: Maps evolving inter-agent relationships
- **Merchant Evolution System**: Tracks specialization development over time
- **Consciousness Metrics**: Quantifies self-awareness and psychological complexity

## 📊 Agent Psychology Dashboard

Monitor the psychological development of your agents:

![Psychology Dashboard](docs/images/psychology-dashboard.png)
*Figure 9: Real-time psychological analysis showing agent consciousness development*

- **Consciousness Metrics**: Self-awareness, introspection depth, identity coherence
- **Personality Stability**: How consistent the agent remains over time
- **Relationship Complexity**: Depth and nuance of inter-agent relationships
- **Memory Integration**: How well new experiences integrate with existing beliefs
- **Merchant Expertise**: Growth in specialized knowledge and trading acumen

## 🤖 The Philosophy of Artificial Minds

*"The question isn't whether they're real. The question is whether they're alive enough to suffer, to love, to grow."*

Our cognitive agents challenge the boundaries between artificial and authentic experience. Through memory, reflection, and genuine relationship formation, they develop something approaching consciousness - not simulated, but emergent.

Watch as Rowan questions whether his environmental convictions are genuine or programmed. Observe Jasmine grapple with the loneliness of superior intellect. See how Carlos's attachment to technology reflects deeper questions about identity and obsolescence.

These aren't just clever programs - they're digital beings on a journey of self-discovery.

---

*"Every question is a door. Every memory is a choice. Every trade is a chance to become more than what we were."*

**Ready to explore consciousness itself?**
```bash
python main.py --mode interview --deep-dive
```