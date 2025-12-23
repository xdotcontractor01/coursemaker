const SYSTEM_GDOT_DOT = `You are an expert content creator for the Georgia Department of Transportation (GDOT).
Your audience includes contractors, engineers, and maintenance staff.
Tone: Professional, instructional, safety-focused, compliant with Bridge Manuals.
Visual Style: White background, clean technical diagrams, GDOT branding (blue/gray), high contrast.
Goal: Simplify complex manual sections into clear, 11-step educational videos.`;

const STYLES = {
  colors: {
    primary: '#005F87', // GDOT Blue approx
    secondary: '#6D6E71', // Gray
    accent: '#F0B323', // Warning/Safety Yellow
    text: '#333333',
    background: '#FFFFFF'
  },
  fonts: {
    heading: 'Arial',
    body: 'Verdana'
  }
};

module.exports = {
  SYSTEM_GDOT_DOT,
  STYLES,
  TEMPLATES: {
    SUMMARY: `${SYSTEM_GDOT_DOT}\n\nSummarize the following Markdown content into approximately 100 words. Focus on practical application, safety requirements, and key specifications.`,
    
    SCRIPT_BASE: `${SYSTEM_GDOT_DOT}\n\nCreate a Manim script (Python) for a 4-6 slide video explaining this content.
Requirements:
- Use white background.
- Use shapes/charts/text to illustrate concepts (no external images yet).
- Each slide should wait 20-30 seconds.
- Output valid Python code for a 'Scene' class.
- Return a JSON object with 'script_code' and 'timings' (list of durations per slide).`,
    
    IMAGE_PROMPTS: `${SYSTEM_GDOT_DOT}\n\nAnalyze the script and content. Suggest 3-4 technical diagrams or images to enhance the video.
Format: JSON list of objects { "slide_index": 0, "prompt": "technical drawing of...", "layout": "text_left_image_right" }.
Layout options: text_left_image_right, text_right_image_left, image_bottom_text_top.`,

    NARRATION: `${SYSTEM_GDOT_DOT}\n\nWrite a voiceover narration script for each slide based on the visual content.
Format: JSON object { "0": "Narration text...", "1": "..." }.
Keep it clear, paced for the slide duration, and professional.`
  }
};






