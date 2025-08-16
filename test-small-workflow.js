/**
 * Generate smaller workflow that fits in URL for direct testing
 */

const fs = require('fs');

// Smaller 8-step workflow
const smallWorkflow = [
  { action: "Open email inbox", application: "Outlook", purpose: "Check orders", time_formatted: "3s", visible_in_frames: [1,2,3] },
  { action: "Select customer email", application: "Outlook", purpose: "Read order", time_formatted: "2s", visible_in_frames: [4,5] },
  { action: "Copy customer details", application: "Outlook", purpose: "Extract info", time_formatted: "2s", visible_in_frames: [6,7] },
  { action: "Open WMS system", application: "Chrome (WMS)", purpose: "Access system", time_formatted: "4s", visible_in_frames: [8,9,10,11] },
  { action: "Create new order", application: "Chrome (WMS)", purpose: "Start entry", time_formatted: "2s", visible_in_frames: [12,13] },
  { action: "Enter customer data", application: "Chrome (WMS)", purpose: "Fill form", time_formatted: "5s", visible_in_frames: [14,15,16,17,18] },
  { action: "Add order items", application: "Chrome (WMS)", purpose: "Specify products", time_formatted: "4s", visible_in_frames: [19,20,21,22] },
  { action: "Submit order", application: "Chrome (WMS)", purpose: "Complete process", time_formatted: "2s", visible_in_frames: [23,24] }
];

// Same DrawioGenerator as before but simpler
class DrawioGenerator {
  generateXML(workflowSteps, title) {
    const nodes = this.createNodes(workflowSteps);
    const edges = this.createEdges(workflowSteps);
    const titleNode = this.createTitleNode(title);
    return this.wrapInMxGraphModel(titleNode + nodes + edges);
  }

  createNodes(steps) {
    const positions = [];
    const baseWidth = 180;
    const baseHeight = 100;
    const spacing = 220;
    const startX = 50;
    const startY = 100;
    
    // 4 steps per row for small workflow
    const stepsPerRow = 4;
    
    steps.forEach((step, index) => {
      const row = Math.floor(index / stepsPerRow);
      const col = index % stepsPerRow;
      
      positions.push({
        x: startX + (col * spacing),
        y: startY + (row * 150),
        width: baseWidth,
        height: baseHeight
      });
    });
    
    return steps.map((step, index) => {
      const pos = positions[index];
      const lines = [
        step.action,
        `📱 ${step.application}`,
        `⏱️ ${step.time_formatted}`
      ];
      const label = lines.join('&#xa;');
      const color = step.application.includes('Outlook') ? '#fff2cc' : '#dae8fc';
      const stroke = step.application.includes('Outlook') ? '#d6b656' : '#6c8ebf';
      
      return `<mxCell id="step${index + 1}" value="${this.escapeXML(label)}" style="rounded=1;whiteSpace=wrap;html=1;fillColor=${color};strokeColor=${stroke};strokeWidth=2;shadow=1;" vertex="1" parent="1"><mxGeometry x="${pos.x}" y="${pos.y}" width="${pos.width}" height="${pos.height}" as="geometry"/></mxCell>`;
    }).join('');
  }

  createEdges(steps) {
    return steps.slice(0, -1).map((step, index) => 
      `<mxCell id="edge${index + 1}" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;endArrow=classic;" source="step${index + 1}" target="step${index + 2}" edge="1" parent="1"><mxGeometry relative="1" as="geometry"/></mxCell>`
    ).join('');
  }

  createTitleNode(title) {
    return `<mxCell id="title" value="${this.escapeXML(title)}" style="text;html=1;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=14;fontStyle=1;" vertex="1" parent="1"><mxGeometry x="50" y="20" width="400" height="30" as="geometry"/></mxCell>`;
  }

  wrapInMxGraphModel(content) {
    return `<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net">
  <diagram id="workflow" name="NewSystem.AI Test">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1200" pageHeight="800">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>${content}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>`;
  }

  escapeXML(text) {
    return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }
}

const generator = new DrawioGenerator();

console.log('🔬 Small Workflow Test (8 steps)');
console.log('=================================\n');

const startTime = process.hrtime.bigint();
const xml = generator.generateXML(smallWorkflow, 'Email-to-WMS Workflow (8 Steps)');
const endTime = process.hrtime.bigint();
const generationTimeMs = Number(endTime - startTime) / 1000000;

// Create URL
const base64 = Buffer.from(xml).toString('base64');
const encoded = encodeURIComponent(base64);
const url = `https://app.diagrams.net/#U${encoded}`;

console.log('📊 Performance:');
console.log(`  XML Generation: ${generationTimeMs.toFixed(2)}ms`);
console.log(`  XML Size: ${(xml.length / 1024).toFixed(1)}KB`);
console.log(`  URL Length: ${url.length} characters`);
console.log(`  URL Safe: ${url.length <= 8000 ? '✅ Yes' : '❌ No'}`);

if (url.length <= 8000) {
  console.log('\n🔗 Direct Draw.io URL:');
  console.log(url);
  console.log('\n📋 Steps to get screenshot:');
  console.log('1. Copy URL above');
  console.log('2. Paste in browser');
  console.log('3. Take screenshot');
  console.log('4. Save as "drawio-8step-proof.png"');
  
  // Also save for easy access
  fs.writeFileSync('small-workflow-url.txt', url);
  console.log('\n💾 URL saved to small-workflow-url.txt');
} else {
  console.log('\n❌ Still too long!');
}

// Show what the layout looks like
console.log('\n🎨 Layout Analysis:');
console.log('  Steps per row: 4');
console.log('  Total rows: 2');
console.log('  Canvas: 1200x800px');
console.log('  Node colors: Yellow (Outlook), Blue (WMS)');
console.log('  Edge style: Sequential arrows');