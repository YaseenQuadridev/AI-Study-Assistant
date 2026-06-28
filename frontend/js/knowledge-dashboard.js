// knowledge-dashboard.js — Document upload, knowledge graph, topic browser

class KnowledgeDashboard {
  constructor(supabaseClient) {
    this.supabase = supabaseClient;
    this.documents = [];
    this.topics = [];
    this.graphData = { nodes: [], edges: [] };
  }

  async loadDocuments() {
    const { data: { user } } = await this.supabase.auth.getUser();
    if (!user) return;
    const { data } = await this.supabase.from("documents").select("*").eq("user_id", user.id).order("created_at", { ascending: false });
    this.documents = data || [];
    this.renderDocumentList();
  }

  renderDocumentList() {
    const container = document.getElementById("doc-list");
    if (!container) return;
    container.innerHTML = "";
    this.documents.forEach(doc => {
      const el = document.createElement("div");
      el.className = "doc-item";
      const statusColor = { ready: "green", error: "red", processing: "orange" }[doc.status] || "gray";
      el.innerHTML = `
        <div class="doc-name">${doc.filename}</div>
        <div class="doc-meta">${doc.status} | ${doc.chunks_count} chunks | ${doc.concepts_count} concepts</div>
        <span class="status-badge ${statusColor}">${doc.status}</span>
      `;
      el.onclick = () => this.showDocumentDetail(doc.id);
      container.appendChild(el);
    });
  }

  renderTopicTree() {
    const container = document.getElementById("topic-tree");
    if (!container) return;
    container.innerHTML = "";
    const subjects = {};
    this.topics.forEach(t => {
      const subj = t.subject || "Uncategorized";
      if (!subjects[subj]) subjects[subj] = [];
      subjects[subj].push(t);
    });
    Object.entries(subjects).forEach(([subject, topics]) => {
      const group = document.createElement("details");
      group.innerHTML = `<summary>${subject} (${topics.length})</summary>`;
      topics.forEach(t => {
        const item = document.createElement("div");
        item.className = "topic-item";
        item.textContent = t.name;
        item.onclick = () => this.searchByTopic(t.name);
        group.appendChild(item);
      });
      container.appendChild(group);
    });
  }

  renderGraph(nodes, edges) {
    const container = document.getElementById("graph-viz");
    if (!container || typeof d3 === "undefined") {
      container.innerHTML = "<p>Graph visualization requires D3.js. Install with: npm install d3</p>";
      return;
    }
    container.innerHTML = "";
    const width = container.clientWidth || 800;
    const height = 500;

    const svg = d3.select(container).append("svg")
      .attr("width", width).attr("height", height);

    const simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(edges).id(d => d.id).distance(100))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2));

    const link = svg.append("g").selectAll("line")
      .data(edges).enter().append("line")
      .attr("stroke", "#999").attr("stroke-width", 2);

    const node = svg.append("g").selectAll("circle")
      .data(nodes).enter().append("circle")
      .attr("r", d => 5 + d.confidence * 10)
      .attr("fill", d => d.type === "concept" ? "#4f46e5" : d.type === "formula" ? "#059669" : "#7c3aed")
      .call(d3.drag().on("start", dragstarted).on("drag", dragged).on("end", dragended));

    node.append("title").text(d => d.label);

    simulation.on("tick", () => {
      link.attr("x1", d => d.source.x).attr("y1", d => d.source.y)
          .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
      node.attr("cx", d => d.x).attr("cy", d => d.y);
    });

    function dragstarted(event, d) { if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; }
    function dragged(event, d) { d.fx = event.x; d.fy = event.y; }
    function dragended(event, d) { if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }
  }

  async searchByTopic(topic) {
    const { data } = await this.supabase.from("chunks").select("*").textSearch("text", topic);
    this.renderSearchResults(data || []);
  }

  renderSearchResults(results) {
    const container = document.getElementById("search-results");
    if (!container) return;
    container.innerHTML = "";
    results.forEach(r => {
      const el = document.createElement("div");
      el.className = "search-result";
      el.innerHTML = `<strong>${r.heading || "Untitled"}</strong><p>${r.text.substring(0, 200)}...</p>`;
      container.appendChild(el);
    });
  }

  async showDocumentDetail(docId) {
    const { data } = await this.supabase.from("documents").select("*").eq("id", docId).single();
    if (!data) return;
    alert(`Document: ${data.filename}\nStatus: ${data.status}\nChunks: ${data.chunks_count}\nConcepts: ${data.concepts_count}\nFormulas: ${data.formulas_count}`);
  }

  setupUploadDragDrop() {
    const zone = document.getElementById("upload-zone");
    if (!zone) return;
    zone.addEventListener("dragover", e => { e.preventDefault(); zone.classList.add("dragover"); });
    zone.addEventListener("dragleave", () => zone.classList.remove("dragover"));
    zone.addEventListener("drop", async (e) => {
      e.preventDefault();
      zone.classList.remove("dragover");
      const files = Array.from(e.dataTransfer.files);
      for (const file of files) {
        await this.uploadFile(file);
      }
    });
  }

  async uploadFile(file) {
    const { data: { user } } = await this.supabase.auth.getUser();
    if (!user) return;
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch("/api/v3/upload", {
      method: "POST",
      headers: { "Authorization": `Bearer ${(await this.supabase.auth.getSession()).data.session.access_token}` },
      body: formData
    });
    const result = await res.json();
    console.log("Upload result:", result);
    this.loadDocuments();
  }
}

window.KnowledgeDashboard = KnowledgeDashboard;
