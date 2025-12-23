import json
from pathlib import Path
from PIL import Image

figures_dir = Path('figures/chapter_01')
metadata = {
    'chapter_id': 'chapter_01',
    'extracted_from': 'BasicHiwyPlanReading (1).pdf',
    'pages': '17-35',
    'images': []
}

# Labels based on the PDF content
labels = {
    'fig_1-1': 'Cover Sheet - Plan View of Project',
    'fig_1-2': 'Cover Sheet Layout View',
    'fig_1-3': 'Cover Sheet Components',
    'fig_1-4': 'Engineers Scale (10 scale)',
    'fig_1-5': 'Engineers Scale (20 scale)',  
    'fig_1-6': 'Bar Scale from Plan Sheet',
    'fig_1-7': 'Index Sheet Example',
    'fig_1-8': 'Revision Summary Sheet',
    'fig_1-9': 'Typical Roadway Cross Section',
    'fig_1-10': 'Scale bar detail',
    'fig_1-11': 'Scale bar detail',
    'fig_1-12': 'Horizontal vs Slope Distance',
    'fig_1-13': 'Plan Sheet Detail',
    'fig_1-14': 'Summary of Quantities',
    'fig_1-15': 'Drainage Summary Sheet',
    'fig_1-16': 'Detailed Estimate Sheet',
}

descriptions = {
    'fig_1-1': 'Highway plan cover sheet showing project overview, location map, and sheet index from GDOT training manual.',
    'fig_1-2': 'Layout view of project showing overall roadway alignment and key features.',
    'fig_1-3': 'Detailed components of a cover sheet including title block and identification information.',
    'fig_1-4': 'Civil engineers scale showing 10 scale measurements for reading plans.',
    'fig_1-5': 'Civil engineers scale showing 20 scale measurements for detailed measurements.',
    'fig_1-6': 'Bar scale (graphical scale) showing feet measurements that adjusts with plan reproduction.',
    'fig_1-7': 'Index sheet listing all sheets in the plan set with their numbers and descriptions.',
    'fig_1-8': 'Revision summary sheet tracking all changes and modifications to the plans.',
    'fig_1-9': 'Typical roadway cross section showing travel lanes, shoulders, slopes, and drainage elements.',
    'fig_1-10': 'Detail of scale bar markings and measurements.',
    'fig_1-11': 'Additional scale bar detail for reference.',
    'fig_1-12': 'Diagram showing difference between horizontal distance and slope distance measurements.',
    'fig_1-13': 'Plan sheet detail showing construction elements and dimensions.',
    'fig_1-14': 'Summary of quantities sheet showing material totals for the project.',
    'fig_1-15': 'Drainage summary sheet showing storm water management details.',
    'fig_1-16': 'Detailed estimate sheet showing item quantities and costs.',
}

key_elements = {
    'fig_1-1': ['project title', 'location map', 'index of sheets', 'project number'],
    'fig_1-2': ['roadway alignment', 'project limits', 'key intersections'],
    'fig_1-3': ['title block', 'engineer seal', 'revision block', 'sheet number'],
    'fig_1-4': ['10 divisions', 'scale markings', 'reading direction'],
    'fig_1-5': ['20 divisions', 'scale markings', 'inch markers'],
    'fig_1-6': ['0-50-100 feet markers', 'graphical scale', 'alternating colors'],
    'fig_1-7': ['sheet numbers', 'sheet descriptions', 'page count'],
    'fig_1-8': ['revision numbers', 'dates', 'descriptions of changes'],
    'fig_1-9': ['travel lanes', 'shoulders', 'slopes', 'ditches', 'right of way'],
    'fig_1-10': ['scale increments', 'measurements'],
    'fig_1-11': ['scale increments'],
    'fig_1-12': ['horizontal distance', 'slope distance', 'grade'],
    'fig_1-13': ['construction details', 'dimensions', 'labels'],
    'fig_1-14': ['item numbers', 'quantities', 'units'],
    'fig_1-15': ['pipe sizes', 'inlet locations', 'drainage areas'],
    'fig_1-16': ['pay items', 'unit prices', 'totals'],
}

for fig_path in sorted(figures_dir.glob('*.png')):
    img = Image.open(fig_path)
    fig_id = fig_path.stem
    
    metadata['images'].append({
        'id': fig_id,
        'path': f'figures/chapter_01/{fig_path.name}',
        'label': labels.get(fig_id, f'Figure {fig_id}'),
        'width': img.size[0],
        'height': img.size[1],
        'description': descriptions.get(fig_id, 'Highway plan figure from the GDOT training manual.'),
        'key_elements': key_elements.get(fig_id, ['title', 'labels', 'scales', 'details']),
        'highlight_suggestions': ['main title', 'key sections', 'important labels']
    })

with open(figures_dir / 'image_metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)

print(f'Updated metadata with {len(metadata["images"])} images')

