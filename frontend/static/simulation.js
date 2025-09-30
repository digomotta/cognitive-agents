// Frontend JavaScript for Markov Agent Simulation

const API_BASE = '';
let selectedAgents = new Set();
let pollingInterval = null;
let eventCounts = { messages: 0, trades: 0, reflections: 0, total: 0 };
let networkSvg = null;
let networkSimulation = null;

// Initialize page
document.addEventListener('DOMContentLoaded', async () => {
    await loadAgents();
    setupEventListeners();
});

// Load available agents
async function loadAgents() {
    try {
        const response = await fetch(`${API_BASE}/api/agents`);
        const data = await response.json();

        const grid = document.getElementById('agents-grid');
        grid.innerHTML = '';

        data.agents.forEach(agent => {
            const card = createAgentCard(agent);
            grid.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading agents:', error);
        document.getElementById('agents-grid').innerHTML = '<p style="color: red;">Error loading agents</p>';
    }
}

// Create agent card
function createAgentCard(agent) {
    const card = document.createElement('div');
    card.className = 'agent-card';
    card.dataset.agentId = agent.id;

    card.innerHTML = `
        <h3>${agent.name}</h3>
        <p><strong>Age:</strong> ${agent.age}</p>
        <p><strong>Occupation:</strong> ${agent.occupation}</p>
        <p><strong>Location:</strong> ${agent.address}</p>
        <p><strong>Items:</strong> ${agent.inventory_count}</p>
        <p style="margin-top: 10px; font-size: 0.85em; font-style: italic;">${agent.self_description.substring(0, 100)}...</p>
    `;

    card.addEventListener('click', () => toggleAgentSelection(card, agent.id));
    return card;
}

// Toggle agent selection
function toggleAgentSelection(card, agentId) {
    if (selectedAgents.has(agentId)) {
        selectedAgents.delete(agentId);
        card.classList.remove('selected');
    } else {
        selectedAgents.add(agentId);
        card.classList.add('selected');
    }

    // Enable start button if at least 2 agents selected
    document.getElementById('start-btn').disabled = selectedAgents.size < 2;
}

// Setup event listeners
function setupEventListeners() {
    document.getElementById('start-btn').addEventListener('click', startSimulation);
}

// Start simulation
async function startSimulation() {
    const config = {
        agents: Array.from(selectedAgents),
        num_steps: parseInt(document.getElementById('num-steps').value),
        max_turns: parseInt(document.getElementById('max-turns').value),
        self_reflection_prob: parseFloat(document.getElementById('self-reflection').value),
        interaction_prob: parseFloat(document.getElementById('interaction-prob').value),
        context: document.getElementById('context').value
    };

    try {
        const response = await fetch(`${API_BASE}/api/simulation/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });

        const data = await response.json();

        if (response.ok) {
            // Switch to simulation page
            document.getElementById('setup-page').style.display = 'none';
            document.getElementById('simulation-page').style.display = 'block';

            // Initialize network visualization
            initializeNetwork();

            // Start polling for events
            startPolling();
        } else {
            alert('Error starting simulation: ' + data.error);
        }
    } catch (error) {
        console.error('Error starting simulation:', error);
        alert('Error starting simulation');
    }
}

// Initialize network visualization
function initializeNetwork() {
    const container = document.getElementById('network-graph');
    const width = container.clientWidth;
    const height = container.clientHeight - 60;

    networkSvg = d3.select('#network-graph')
        .attr('width', width)
        .attr('height', height);

    // Create arrow marker for directed edges
    networkSvg.append('defs').append('marker')
        .attr('id', 'arrowhead')
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 20)
        .attr('refY', 0)
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .attr('orient', 'auto')
        .append('path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('fill', '#999');

    // Initialize force simulation
    networkSimulation = d3.forceSimulation()
        .force('link', d3.forceLink().id(d => d.id).distance(150))
        .force('charge', d3.forceManyBody().strength(-500))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(50));

    loadNetworkData();
}

// Load and update network data
async function loadNetworkData() {
    try {
        const response = await fetch(`${API_BASE}/api/network`);
        const data = await response.json();

        updateNetwork(data.network);
    } catch (error) {
        console.error('Error loading network:', error);
    }
}

// Update network visualization
function updateNetwork(networkData) {
    if (!networkData.nodes || networkData.nodes.length === 0) return;

    // Clear existing
    networkSvg.selectAll('*').filter(function() {
        return this.tagName !== 'defs';
    }).remove();

    // Create links
    const links = networkSvg.append('g')
        .selectAll('line')
        .data(networkData.edges)
        .enter().append('line')
        .attr('stroke', '#999')
        .attr('stroke-opacity', d => d.weight * 2)
        .attr('stroke-width', d => Math.max(1, d.weight * 5))
        .attr('marker-end', 'url(#arrowhead)');

    // Create nodes
    const nodes = networkSvg.append('g')
        .selectAll('g')
        .data(networkData.nodes)
        .enter().append('g')
        .call(d3.drag()
            .on('start', dragStarted)
            .on('drag', dragged)
            .on('end', dragEnded));

    // Node circles (size based on sales)
    nodes.append('circle')
        .attr('r', d => Math.max(20, 20 + Math.sqrt(d.sales) / 2))
        .attr('fill', d => d3.interpolateRdYlGn((d.net_value + 500) / 1000))
        .attr('stroke', '#fff')
        .attr('stroke-width', 3);

    // Node labels
    nodes.append('text')
        .text(d => d.id.split(' ')[0])
        .attr('text-anchor', 'middle')
        .attr('dy', 4)
        .attr('font-size', '12px')
        .attr('font-weight', 'bold')
        .attr('fill', '#333')
        .attr('pointer-events', 'none');

    // Update simulation
    networkSimulation.nodes(networkData.nodes);
    networkSimulation.force('link').links(networkData.edges);
    networkSimulation.alpha(0.3).restart();

    // Update positions on each tick
    networkSimulation.on('tick', () => {
        links
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        nodes.attr('transform', d => `translate(${d.x},${d.y})`);
    });
}

// Drag functions
function dragStarted(event, d) {
    if (!event.active) networkSimulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
}

function dragEnded(event, d) {
    if (!event.active) networkSimulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}

// Start polling for events
function startPolling() {
    pollingInterval = setInterval(async () => {
        await pollEvents();
        await updateLeaderboard();
        await updateStatus();

        // Update network every 5 seconds
        if (eventCounts.total % 10 === 0) {
            await loadNetworkData();
        }
    }, 1000); // Poll every 1 second
}

// Poll for new events
async function pollEvents() {
    try {
        const response = await fetch(`${API_BASE}/api/events`);
        const data = await response.json();

        data.events.forEach(event => {
            eventCounts.total++;
            handleEvent(event);
        });
    } catch (error) {
        console.error('Error polling events:', error);
    }
}

// Handle individual event
function handleEvent(event) {
    const feed = document.getElementById('messages-feed');

    if (event.type === 'utterance') {
        eventCounts.messages++;

        // Check if this is the first turn of a new conversation
        const data = event.data;
        if (data.conversation_turn === 0) {
            // Add conversation header
            const headerDiv = createConversationHeaderElement(data);
            feed.appendChild(headerDiv);
        }

        const messageDiv = createMessageElement(event);
        feed.appendChild(messageDiv);

    } else if (event.type === 'trade') {
        eventCounts.trades++;
        const tradeDiv = createTradeElement(event);
        feed.appendChild(tradeDiv);

    } else if (event.type === 'reflection') {
        eventCounts.reflections++;
        const reflectionDiv = createReflectionElement(event);
        feed.appendChild(reflectionDiv);
    }

    // Auto-scroll to bottom
    feed.scrollTop = feed.scrollHeight;
}

// Create conversation header element
function createConversationHeaderElement(data) {
    const div = document.createElement('div');
    div.className = 'conversation-header';

    const [agent1, agent2] = data.participants;

    div.innerHTML = `
        <div style="text-align: center; padding: 15px 20px; margin: 15px 0 10px 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white; font-weight: 600; font-size: 1.1em; box-shadow: 0 3px 10px rgba(102, 126, 234, 0.3);">
            <span style="margin-right: 10px;">💬</span>
            <span>${agent1}</span>
            <span style="margin: 0 15px; font-size: 1.2em;">→</span>
            <span>${agent2}</span>
            <span style="margin-left: 10px; font-size: 0.85em; opacity: 0.9;">(Step ${data.markov_step})</span>
        </div>
    `;

    return div;
}

// Create message element
function createMessageElement(event) {
    const data = event.data;
    const div = document.createElement('div');
    div.className = 'message-item';

    div.innerHTML = `
        <div class="message-header">
            <span>Step ${data.markov_step} • Turn ${data.conversation_turn}</span>
            <span>${new Date(event.timestamp * 1000).toLocaleTimeString()}</span>
        </div>
        <div class="message-agent">${data.agent}</div>
        <div class="message-text">${data.text}</div>
    `;

    return div;
}

// Create trade element
function createTradeElement(event) {
    const data = event.data;
    const details = data.trade_details;
    const participants = details.participants;
    const items = details.items;

    const div = document.createElement('div');
    div.className = 'message-item trade';

    const itemsList = items.map(item =>
        `${item.quantity} ${item.name} ($${item.value})`
    ).join(', ');

    div.innerHTML = `
        <div class="message-header">
            <span>Step ${data.markov_step} • Turn ${data.conversation_turn} <span class="trade-badge">TRADE</span></span>
            <span>${new Date(event.timestamp * 1000).toLocaleTimeString()}</span>
        </div>
        <div class="message-agent">${participants.seller} → ${participants.buyer}</div>
        <div class="message-text">${itemsList}</div>
    `;

    return div;
}

// Create reflection element
function createReflectionElement(event) {
    const data = event.data;
    const div = document.createElement('div');
    div.className = 'message-item reflection';

    // Build thoughts list
    let thoughtsHtml = '';
    if (data.thoughts && data.thoughts.length > 0) {
        thoughtsHtml = '<div style="margin-top: 10px;"><strong>Thoughts:</strong><ul style="margin: 5px 0 0 20px; line-height: 1.6;">';
        data.thoughts.forEach(thought => {
            thoughtsHtml += `<li>${thought}</li>`;
        });
        thoughtsHtml += '</ul></div>';
    }

    div.innerHTML = `
        <div class="message-header">
            <span>Step ${data.markov_step} <span style="background: #ffc107; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.8em;">REFLECTION</span></span>
            <span>${new Date(event.timestamp * 1000).toLocaleTimeString()}</span>
        </div>
        <div class="message-agent">${data.agent}</div>
        <div class="message-text">
            <div><strong>Reflecting on:</strong> ${data.anchor}</div>
            ${thoughtsHtml}
        </div>
    `;

    return div;
}

// Update leaderboard
async function updateLeaderboard() {
    try {
        const response = await fetch(`${API_BASE}/api/leaderboard`);
        const data = await response.json();

        const container = document.getElementById('leaderboard');

        if (data.leaderboard.length === 0) {
            container.innerHTML = '<div class="loading">Waiting for trades...</div>';
            return;
        }

        container.innerHTML = '';

        data.leaderboard.forEach((entry, index) => {
            const div = document.createElement('div');
            div.className = 'leaderboard-item';

            const medal = index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `${index + 1}.`;

            div.innerHTML = `
                <div class="leaderboard-name">${medal} ${entry.agent}</div>
                <div class="leaderboard-stats">
                    Sales: $${entry.sales.toFixed(2)} •
                    Purchases: $${entry.purchases.toFixed(2)} •
                    Net: $${entry.net_value.toFixed(2)}
                </div>
            `;

            container.appendChild(div);
        });
    } catch (error) {
        console.error('Error updating leaderboard:', error);
    }
}

// Update status panel
async function updateStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/simulation/status`);
        const data = await response.json();

        document.getElementById('status-running').textContent = data.running ? 'Running' : 'Completed';
        document.getElementById('status-events').textContent = eventCounts.total;
        document.getElementById('status-messages').textContent = eventCounts.messages;
        document.getElementById('status-trades').textContent = eventCounts.trades;
        document.getElementById('status-reflections').textContent = eventCounts.reflections;

        // Stop polling if simulation finished
        if (!data.running && pollingInterval) {
            setTimeout(() => {
                clearInterval(pollingInterval);
                console.log('Simulation completed');
            }, 5000); // Keep polling for 5 more seconds to catch final events
        }
    } catch (error) {
        console.error('Error updating status:', error);
    }
}