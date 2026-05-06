import { useRef, useEffect, useCallback } from 'react';

export default function NetworkGraph({ graphData, height = 400 }) {
  const canvasRef = useRef(null);
  const animRef = useRef(null);
  const nodesRef = useRef([]);
  const edgesRef = useRef([]);
  const dragRef = useRef({ node: null, offsetX: 0, offsetY: 0 });
  const hoverRef = useRef(null);

  // Initialize node positions
  useEffect(() => {
    if (!graphData?.nodes?.length) return;

    const w = canvasRef.current?.parentElement?.clientWidth || 600;
    const h = height;
    const cx = w / 2;
    const cy = h / 2;
    const radius = Math.min(w, h) * 0.35;

    nodesRef.current = graphData.nodes.map((node, i) => {
      const angle = (2 * Math.PI * i) / graphData.nodes.length;
      return {
        ...node,
        x: cx + radius * Math.cos(angle) + (Math.random() - 0.5) * 40,
        y: cy + radius * Math.sin(angle) + (Math.random() - 0.5) * 40,
        vx: 0, vy: 0,
      };
    });

    edgesRef.current = (graphData.edges || []).map(e => ({
      ...e,
      source: typeof e.source === 'string' ? e.source : e.source,
      target: typeof e.target === 'string' ? e.target : e.target,
    }));
  }, [graphData, height]);

  // Force simulation
  const simulate = useCallback(() => {
    const nodes = nodesRef.current;
    const edges = edgesRef.current;
    if (!nodes.length) return;

    const w = canvasRef.current?.width || 600;
    const h = canvasRef.current?.height || 400;

    // Repulsion
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const dx = nodes[j].x - nodes[i].x;
        const dy = nodes[j].y - nodes[i].y;
        const dist = Math.max(Math.sqrt(dx * dx + dy * dy), 1);
        const force = 2000 / (dist * dist);
        const fx = (dx / dist) * force;
        const fy = (dy / dist) * force;
        nodes[i].vx -= fx;
        nodes[i].vy -= fy;
        nodes[j].vx += fx;
        nodes[j].vy += fy;
      }
    }

    // Attraction along edges
    const nodeMap = {};
    nodes.forEach(n => { nodeMap[n.id] = n; });

    edges.forEach(e => {
      const s = nodeMap[e.source];
      const t = nodeMap[e.target];
      if (!s || !t) return;
      const dx = t.x - s.x;
      const dy = t.y - s.y;
      const dist = Math.max(Math.sqrt(dx * dx + dy * dy), 1);
      const force = (dist - 120) * 0.02;
      const fx = (dx / dist) * force;
      const fy = (dy / dist) * force;
      s.vx += fx; s.vy += fy;
      t.vx -= fx; t.vy -= fy;
    });

    // Center gravity
    const cx = w / 2;
    const cy = h / 2;
    nodes.forEach(n => {
      n.vx += (cx - n.x) * 0.002;
      n.vy += (cy - n.y) * 0.002;
      n.vx *= 0.85;
      n.vy *= 0.85;
      if (dragRef.current.node !== n) {
        n.x += n.vx;
        n.y += n.vy;
      }
      n.x = Math.max(30, Math.min(w - 30, n.x));
      n.y = Math.max(30, Math.min(h - 30, n.y));
    });
  }, []);

  // Render loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const parentW = canvas.parentElement.clientWidth;
    canvas.width = parentW;
    canvas.height = height;

    let running = true;
    const draw = () => {
      if (!running) return;
      simulate();

      const w = canvas.width;
      const h = canvas.height;
      ctx.clearRect(0, 0, w, h);

      const nodes = nodesRef.current;
      const edges = edgesRef.current;
      const nodeMap = {};
      nodes.forEach(n => { nodeMap[n.id] = n; });

      // Draw edges
      edges.forEach(e => {
        const s = nodeMap[e.source];
        const t = nodeMap[e.target];
        if (!s || !t) return;
        const weight = e.weight || 0.5;
        const alpha = 0.15 + weight * 0.4;
        // Color by weight (low weight = green/good diversification, high = red)
        const r = Math.floor(16 + weight * 200);
        const g = Math.floor(185 - weight * 150);
        const b = Math.floor(129 - weight * 80);
        ctx.beginPath();
        ctx.moveTo(s.x, s.y);
        ctx.lineTo(t.x, t.y);
        ctx.strokeStyle = `rgba(${r},${g},${b},${alpha})`;
        ctx.lineWidth = 1 + weight * 1.5;
        ctx.stroke();
      });

      // Draw nodes
      nodes.forEach(n => {
        const isHover = hoverRef.current === n.id;
        const r = isHover ? 18 : 14;

        // Glow
        const gradient = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, r * 2);
        gradient.addColorStop(0, 'rgba(59,130,246,0.15)');
        gradient.addColorStop(1, 'rgba(59,130,246,0)');
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(n.x, n.y, r * 2, 0, Math.PI * 2);
        ctx.fill();

        // Node circle
        ctx.beginPath();
        ctx.arc(n.x, n.y, r, 0, Math.PI * 2);
        ctx.fillStyle = isHover ? '#3b82f6' : '#1e3a5f';
        ctx.fill();
        ctx.strokeStyle = isHover ? '#60a5fa' : '#3b82f6';
        ctx.lineWidth = 2;
        ctx.stroke();

        // Label
        ctx.fillStyle = '#f1f5f9';
        ctx.font = `${isHover ? '600' : '500'} ${isHover ? 11 : 10}px Inter, sans-serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(n.id || n.label || '', n.x, n.y);
      });

      animRef.current = requestAnimationFrame(draw);
    };
    draw();

    // Mouse handlers for drag
    const getNode = (mx, my) => {
      return nodesRef.current.find(n => {
        const dx = n.x - mx, dy = n.y - my;
        return dx * dx + dy * dy < 400;
      });
    };

    const onMouseDown = (e) => {
      const rect = canvas.getBoundingClientRect();
      const node = getNode(e.clientX - rect.left, e.clientY - rect.top);
      if (node) dragRef.current = { node, offsetX: 0, offsetY: 0 };
    };
    const onMouseMove = (e) => {
      const rect = canvas.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;
      const hover = getNode(mx, my);
      hoverRef.current = hover?.id || null;
      canvas.style.cursor = hover ? 'grab' : 'default';
      if (dragRef.current.node) {
        dragRef.current.node.x = mx;
        dragRef.current.node.y = my;
        canvas.style.cursor = 'grabbing';
      }
    };
    const onMouseUp = () => { dragRef.current.node = null; };

    canvas.addEventListener('mousedown', onMouseDown);
    canvas.addEventListener('mousemove', onMouseMove);
    canvas.addEventListener('mouseup', onMouseUp);
    canvas.addEventListener('mouseleave', onMouseUp);

    const handleResize = () => {
      canvas.width = canvas.parentElement.clientWidth;
    };
    window.addEventListener('resize', handleResize);

    return () => {
      running = false;
      cancelAnimationFrame(animRef.current);
      canvas.removeEventListener('mousedown', onMouseDown);
      canvas.removeEventListener('mousemove', onMouseMove);
      canvas.removeEventListener('mouseup', onMouseUp);
      canvas.removeEventListener('mouseleave', onMouseUp);
      window.removeEventListener('resize', handleResize);
    };
  }, [height, simulate]);

  if (!graphData?.nodes?.length) {
    return <div style={{ color: '#64748b', textAlign: 'center', padding: 40 }}>No graph data</div>;
  }

  return (
    <canvas
      ref={canvasRef}
      id="mst-network-graph"
      style={{ width: '100%', borderRadius: 'var(--radius-lg)', display: 'block' }}
    />
  );
}
