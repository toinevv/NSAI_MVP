/**
 * Generate actual Draw.io XML and test URL generation
 * This will create a real URL we can open and screenshot
 */

const fs = require('fs');

// Real workflow data from actual NewSystem.AI analysis
const realWorkflow30Steps = [
  // Email checking phase
  { action: "Open Outlook inbox", application: "Microsoft Outlook", purpose: "Check for new customer orders", time_formatted: "5s", visible_in_frames: [1,2,3,4,5] },
  { action: "Sort emails by date", application: "Microsoft Outlook", purpose: "Prioritize recent orders", time_formatted: "2s", visible_in_frames: [6,7] },
  { action: "Filter for customer orders", application: "Microsoft Outlook", purpose: "Find relevant emails", time_formatted: "3s", visible_in_frames: [8,9,10] },
  { action: "Open first order email", application: "Microsoft Outlook", purpose: "Review order details", time_formatted: "2s", visible_in_frames: [11,12] },
  { action: "Copy customer name", application: "Microsoft Outlook", purpose: "Extract customer info", time_formatted: "2s", visible_in_frames: [13,14] },
  
  // Excel verification phase
  { action: "Switch to Excel", application: "Microsoft Excel", purpose: "Access customer database", time_formatted: "2s", visible_in_frames: [15,16] },
  { action: "Open customer list", application: "Microsoft Excel", purpose: "Verify customer exists", time_formatted: "3s", visible_in_frames: [17,18,19] },
  { action: "Search for customer", application: "Microsoft Excel", purpose: "Find customer record", time_formatted: "4s", visible_in_frames: [20,21,22,23] },
  { action: "Verify customer details", application: "Microsoft Excel", purpose: "Confirm address matches", time_formatted: "3s", visible_in_frames: [24,25,26] },
  { action: "Copy customer ID", application: "Microsoft Excel", purpose: "Get unique identifier", time_formatted: "2s", visible_in_frames: [27,28] },
  
  // Return to email
  { action: "Switch back to Outlook", application: "Microsoft Outlook", purpose: "Continue order processing", time_formatted: "1s", visible_in_frames: [29] },
  { action: "Copy order items", application: "Microsoft Outlook", purpose: "Extract product list", time_formatted: "5s", visible_in_frames: [30,31,32,33,34] },
  { action: "Copy quantities", application: "Microsoft Outlook", purpose: "Get order amounts", time_formatted: "3s", visible_in_frames: [35,36,37] },
  { action: "Copy delivery address", application: "Microsoft Outlook", purpose: "Get shipping info", time_formatted: "3s", visible_in_frames: [38,39,40] },
  { action: "Copy special instructions", application: "Microsoft Outlook", purpose: "Note delivery requirements", time_formatted: "2s", visible_in_frames: [41,42] },
  
  // WMS entry phase
  { action: "Open Chrome browser", application: "Chrome Browser", purpose: "Access WMS system", time_formatted: "3s", visible_in_frames: [43,44,45] },
  { action: "Navigate to WMS portal", application: "Chrome Browser (WMS)", purpose: "Load warehouse system", time_formatted: "4s", visible_in_frames: [46,47,48,49] },
  { action: "Login to WMS", application: "Chrome Browser (WMS)", purpose: "Authenticate user", time_formatted: "3s", visible_in_frames: [50,51,52] },
  { action: "Navigate to new order", application: "Chrome Browser (WMS)", purpose: "Access order entry form", time_formatted: "2s", visible_in_frames: [53,54] },
  { action: "Paste customer ID", application: "Chrome Browser (WMS)", purpose: "Link to customer record", time_formatted: "1s", visible_in_frames: [55] },
  
  // Data entry phase
  { action: "Enter order items", application: "Chrome Browser (WMS)", purpose: "Input product codes", time_formatted: "8s", visible_in_frames: [56,57,58,59,60,61,62,63] },
  { action: "Enter quantities", application: "Chrome Browser (WMS)", purpose: "Specify amounts", time_formatted: "4s", visible_in_frames: [64,65,66,67] },
  { action: "Enter delivery address", application: "Chrome Browser (WMS)", purpose: "Set shipping destination", time_formatted: "5s", visible_in_frames: [68,69,70,71,72] },
  { action: "Add special instructions", application: "Chrome Browser (WMS)", purpose: "Note delivery requirements", time_formatted: "3s", visible_in_frames: [73,74,75] },
  { action: "Select shipping method", application: "Chrome Browser (WMS)", purpose: "Choose delivery speed", time_formatted: "2s", visible_in_frames: [76,77] },
  
  // Validation and submission
  { action: "Review order summary", application: "Chrome Browser (WMS)", purpose: "Verify all details correct", time_formatted: "4s", visible_in_frames: [78,79,80,81] },
  { action: "Calculate shipping cost", application: "Chrome Browser (WMS)", purpose: "Determine delivery charges", time_formatted: "2s", visible_in_frames: [82,83] },
  { action: "Submit order to warehouse", application: "Chrome Browser (WMS)", purpose: "Send to fulfillment", time_formatted: "2s", visible_in_frames: [84,85] },
  { action: "Copy order confirmation", application: "Chrome Browser (WMS)", purpose: "Get tracking number", time_formatted: "2s", visible_in_frames: [86,87] },
  { action: "Return to Outlook", application: "Microsoft Outlook", purpose: "Send confirmation email", time_formatted: "2s", visible_in_frames: [88,89] }
];

// DrawioGenerator implementation
class DrawioGenerator {
  generateXML(workflowSteps, title) {
    const nodes = this.createNodes(workflowSteps);
    const edges = this.createEdges(workflowSteps);
    const titleNode = this.createTitleNode(title);
    return this.wrapInMxGraphModel(titleNode + nodes + edges);
  }

  createNodes(steps) {
    const layout = this.calculateSmartLayout(steps);
    
    return steps.map((step, index) => {
      const stepId = `step${index + 1}`;
      const position = layout.positions[index];
      const lines = this.createProfessionalLabel(step);
      const label = lines.join('&#xa;');
      const style = this.getProfessionalStyle(step);
      
      return `
    <mxCell id="${stepId}" value="${this.escapeXML(label)}" 
           style="${style}" 
           vertex="1" parent="1">
      <mxGeometry x="${position.x}" y="${position.y}" width="${position.width}" height="${position.height}" as="geometry"/>
    </mxCell>`;
    }).join('');
  }

  calculateSmartLayout(steps) {
    const positions = [];
    const baseWidth = 200;
    const baseHeight = 120;
    const horizontalSpacing = 250;
    const verticalSpacing = 180;
    const startX = 50;
    const startY = 100;
    
    let currentX = startX;
    let currentY = startY;
    let maxY = startY;
    
    // Dynamic steps per row based on workflow size
    let maxStepsPerRow;
    if (steps.length <= 10) {
      maxStepsPerRow = 4;
    } else if (steps.length <= 30) {
      maxStepsPerRow = 5;
    } else if (steps.length <= 60) {
      maxStepsPerRow = 6;
    } else {
      maxStepsPerRow = 8;
    }
    
    console.log(`Layout: ${steps.length} steps, ${maxStepsPerRow} per row, ~${Math.ceil(steps.length/maxStepsPerRow)} rows`);
    
    steps.forEach((step, index) => {
      const contentLength = step.action.length + step.application.length;
      const width = Math.max(baseWidth, Math.min(300, baseWidth + Math.floor(contentLength * 0.8)));
      const lines = this.createProfessionalLabel(step);
      const height = Math.max(baseHeight, baseHeight + ((lines.length - 3) * 20));
      
      if (index > 0 && index % maxStepsPerRow === 0) {
        currentX = startX;
        currentY = maxY + verticalSpacing;
      }
      
      positions.push({
        x: currentX,
        y: currentY,
        width: width,
        height: height
      });
      
      currentX += width + horizontalSpacing;
      maxY = Math.max(maxY, currentY + height);
    });
    
    return {
      positions,
      canvasWidth: Math.max(1400, Math.max(...positions.map(p => p.x + p.width)) + 100),
      canvasHeight: maxY + 200
    };
  }

  createProfessionalLabel(step) {
    const lines = [];
    lines.push(step.action);
    if (step.application) {
      lines.push(`📱 ${step.application}`);
    }
    if (step.time_formatted) {
      lines.push(`⏱️ ${step.time_formatted}`);
    }
    if (step.purpose && step.purpose.length < 50) {
      lines.push(`💡 ${step.purpose}`);
    }
    return lines;
  }

  getProfessionalStyle(step) {
    const baseStyle = 'rounded=1;whiteSpace=wrap;html=1;fontFamily=Arial;fontSize=11;spacing=4;';
    const fillColor = this.getNodeColor(step.application);
    const strokeColor = this.getStrokeColor(fillColor);
    return `${baseStyle}fillColor=${fillColor};strokeColor=${strokeColor};strokeWidth=2;shadow=1;glass=0;`;
  }

  getNodeColor(application) {
    const app = (application || '').toLowerCase();
    if (app.includes('outlook') || app.includes('mail')) return '#fff2cc';
    if (app.includes('excel') || app.includes('sheets')) return '#d5e8d4';
    if (app.includes('chrome') || app.includes('wms')) return '#dae8fc';
    if (app.includes('sap') || app.includes('erp')) return '#f8cecc';
    return '#e1d5e7';
  }

  getStrokeColor(fillColor) {
    const strokeMap = {
      '#fff2cc': '#d6b656',
      '#d5e8d4': '#82b366',
      '#dae8fc': '#6c8ebf',
      '#f8cecc': '#b85450',
      '#e1d5e7': '#9673a6'
    };
    return strokeMap[fillColor] || '#666666';
  }

  createEdges(steps) {
    if (steps.length <= 1) return '';
    
    const edges = [];
    steps.slice(0, -1).forEach((step, index) => {
      const edgeId = `edge${index + 1}`;
      const sourceId = `step${index + 1}`;
      const targetId = `step${index + 2}`;
      const edgeStyle = this.getEdgeStyle(step, steps[index + 1]);
      
      edges.push(`
    <mxCell id="${edgeId}" style="${edgeStyle}" 
           source="${sourceId}" target="${targetId}" edge="1" parent="1">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>`);
    });
    
    return edges.join('');
  }

  getEdgeStyle(fromStep, toStep) {
    const baseStyle = 'edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;';
    if (fromStep.application === toStep.application) {
      return `${baseStyle}strokeColor=#82b366;strokeWidth=2;dashed=1;dashPattern=5 5;`;
    } else {
      return `${baseStyle}strokeColor=#666666;strokeWidth=2;endArrow=classic;endFill=1;`;
    }
  }

  createTitleNode(title) {
    return `
    <mxCell id="title" value="${this.escapeXML(title)}" 
           style="text;html=1;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=16;fontStyle=1;fillColor=none;strokeColor=none;" 
           vertex="1" parent="1">
      <mxGeometry x="50" y="20" width="600" height="40" as="geometry"/>
    </mxCell>`;
  }

  wrapInMxGraphModel(content) {
    return `<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net">
  <diagram id="workflow" name="NewSystem.AI Workflow">
    <mxGraphModel dx="2000" dy="1200" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="2000" pageHeight="1400">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>${content}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>`;
  }

  escapeXML(text) {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }
}

// Generate and test
const generator = new DrawioGenerator();

console.log('\n🔬 REAL Draw.io Generation Test');
console.log('================================\n');

// Test with 30-step realistic workflow
const startTime = performance.now();
const xml = generator.generateXML(realWorkflow30Steps, 'Email-to-WMS Order Processing Workflow (30 Steps)');
const generationTime = performance.now() - startTime;

// Encode for URL
const startEncode = performance.now();
const base64 = Buffer.from(xml).toString('base64');
const encoded = encodeURIComponent(base64);
const encodeTime = performance.now() - startEncode;

const url = `https://app.diagrams.net/#U${encoded}`;
const totalTime = generationTime + encodeTime;

console.log('📊 Performance Metrics:');
console.log(`  XML Generation: ${generationTime.toFixed(2)}ms`);
console.log(`  URL Encoding: ${encodeTime.toFixed(2)}ms`);
console.log(`  Total Time: ${totalTime.toFixed(2)}ms`);
console.log(`  XML Size: ${(xml.length / 1024).toFixed(1)}KB`);
console.log(`  URL Length: ${url.length} characters`);
console.log(`  URL Safe: ${url.length <= 8000 ? '✅ Yes' : '❌ No (too long)'}`);

if (url.length <= 8000) {
  console.log('\n🔗 Draw.io URL (copy and paste in browser):');
  console.log(url);
  console.log('\n📸 After opening, take a screenshot!');
} else {
  console.log('\n❌ URL too long for direct opening.');
  console.log('💾 Saving as file instead...');
  fs.writeFileSync('workflow-test.drawio', xml);
  console.log('✅ Saved as workflow-test.drawio - open this file in Draw.io');
}

// Also save the URL to a file for easy access
fs.writeFileSync('drawio-test-url.txt', url);
console.log('\n📝 URL also saved to drawio-test-url.txt');

console.log('\n⚠️ IMPORTANT: Take a screenshot after opening in Draw.io!');
console.log('Use Cmd+Shift+4 (Mac) or Windows+Shift+S (Windows)');