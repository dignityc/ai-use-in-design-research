const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

async function analyzeGanttColors() {
    console.log('🔍 Analyzing actual Mermaid gantt chart colors...\n');
    
    const browser = await puppeteer.launch({ 
        headless: false, // 브라우저 창을 보여줌
        devtools: true   // 개발자 도구 자동 열기
    });
    
    const page = await browser.newPage();
    
    // HTML 파일 경로
    const htmlPath = path.join(__dirname, '..', 'output', 'project_gantt_chart.html');
    const fileUrl = `file://${htmlPath}`;
    
    console.log(`📂 Loading file: ${fileUrl}`);
    await page.goto(fileUrl, { waitUntil: 'networkidle0' });
    
    // Mermaid가 완전히 렌더링될 때까지 대기
    console.log('⏳ Waiting for Mermaid to render...');
    await page.waitForSelector('.mermaid svg', { timeout: 10000 });
    await page.waitForTimeout(3000); // 추가 렌더링 시간
    
    // 실제 SVG 색상 분석
    const colorAnalysis = await page.evaluate(() => {
        const svg = document.querySelector('.mermaid svg');
        if (!svg) return { error: 'SVG not found' };
        
        const results = {
            critical: [],
            milestone: [],
            regular: [],
            sections: []
        };
        
        // 모든 rect 요소 분석
        const rects = svg.querySelectorAll('rect');
        console.log(`Found ${rects.length} rect elements`);
        
        rects.forEach((rect, index) => {
            const fill = rect.getAttribute('fill') || rect.style.fill || window.getComputedStyle(rect).fill;
            const classes = rect.getAttribute('class') || '';
            const id = rect.getAttribute('id') || '';
            
            const info = {
                index,
                fill,
                classes,
                id,
                width: rect.getAttribute('width'),
                height: rect.getAttribute('height'),
                x: rect.getAttribute('x'),
                y: rect.getAttribute('y')
            };
            
            // 작업 바 높이로 필터링 (일반적으로 height="20" 또는 비슷한 값)
            const height = parseInt(rect.getAttribute('height') || '0');
            
            if (height >= 15 && height <= 25) { // 작업 바로 추정
                if (classes.includes('crit') || id.includes('crit')) {
                    results.critical.push(info);
                } else if (classes.includes('milestone') || id.includes('milestone')) {
                    results.milestone.push(info);
                } else {
                    results.regular.push(info);
                }
            } else if (height > 50) { // 섹션 배경으로 추정
                results.sections.push(info);
            }
        });
        
        // 모든 요소의 색상 정보도 수집
        const allColors = Array.from(rects).map((rect, index) => ({
            index,
            fill: rect.getAttribute('fill') || rect.style.fill || window.getComputedStyle(rect).fill,
            classes: rect.getAttribute('class') || '',
            id: rect.getAttribute('id') || '',
            tagName: rect.tagName,
            width: rect.getAttribute('width'),
            height: rect.getAttribute('height')
        }));
        
        return {
            categorized: results,
            allColors: allColors,
            totalElements: rects.length
        };
    });
    
    console.log('\n📊 Color Analysis Results:');
    console.log('='.repeat(50));
    
    if (colorAnalysis.error) {
        console.error('❌ Error:', colorAnalysis.error);
        await browser.close();
        return;
    }
    
    console.log(`\n🔴 Critical Tasks (${colorAnalysis.categorized.critical.length}):`);
    colorAnalysis.categorized.critical.forEach((item, idx) => {
        console.log(`  ${idx + 1}. Fill: ${item.fill} | Classes: "${item.classes}" | ID: "${item.id}"`);
    });
    
    console.log(`\n🟡 Milestone Tasks (${colorAnalysis.categorized.milestone.length}):`);
    colorAnalysis.categorized.milestone.forEach((item, idx) => {
        console.log(`  ${idx + 1}. Fill: ${item.fill} | Classes: "${item.classes}" | ID: "${item.id}"`);
    });
    
    console.log(`\n🔵 Regular Tasks (${colorAnalysis.categorized.regular.length}):`);
    colorAnalysis.categorized.regular.forEach((item, idx) => {
        console.log(`  ${idx + 1}. Fill: ${item.fill} | Classes: "${item.classes}" | ID: "${item.id}"`);
    });
    
    console.log(`\n🟣 Section Backgrounds (${colorAnalysis.categorized.sections.length}):`);
    colorAnalysis.categorized.sections.forEach((item, idx) => {
        console.log(`  ${idx + 1}. Fill: ${item.fill} | Classes: "${item.classes}" | ID: "${item.id}"`);
    });
    
    // 고유한 색상 추출
    const uniqueColors = [...new Set(colorAnalysis.allColors.map(item => item.fill))];
    console.log(`\n🎨 All Unique Colors Found (${uniqueColors.length}):`);
    uniqueColors.forEach((color, idx) => {
        if (color && color !== 'none' && !color.includes('url(')) {
            console.log(`  ${idx + 1}. ${color}`);
        }
    });
    
    // 결과를 파일로 저장
    const outputPath = path.join(__dirname, '..', 'output', 'gantt_color_analysis.json');
    fs.writeFileSync(outputPath, JSON.stringify(colorAnalysis, null, 2));
    console.log(`\n💾 Detailed analysis saved to: ${outputPath}`);
    
    // 추천 색상 생성
    console.log('\n💡 Recommended Legend Colors:');
    console.log('='.repeat(50));
    
    const criticalColor = colorAnalysis.categorized.critical[0]?.fill || '#ff6b6b';
    const milestoneColor = colorAnalysis.categorized.milestone[0]?.fill || '#feca57';
    const regularColor = colorAnalysis.categorized.regular[0]?.fill || '#48dbfb';
    
    console.log(`Critical: ${criticalColor}`);
    console.log(`Milestone: ${milestoneColor}`);
    console.log(`Regular: ${regularColor}`);
    
    // CSS 업데이트 코드 생성
    const cssUpdate = `
/* Updated legend colors based on actual Mermaid rendering */
.critical { background: ${criticalColor}; }
.milestone { background: ${milestoneColor}; }
.task { background: ${regularColor}; }
    `.trim();
    
    console.log('\n🔧 CSS Update Code:');
    console.log(cssUpdate);
    
    console.log('\n✨ Analysis complete! Press Ctrl+C to close browser when done inspecting.');
    
    // 브라우저를 열어둬서 수동으로 확인할 수 있게 함
    // await browser.close();
}

// 실행
analyzeGanttColors().catch(console.error);