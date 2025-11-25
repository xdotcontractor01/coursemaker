"""
Shared utilities and configuration for workflow test scripts
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# ==================== CONFIGURATION ====================
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
SERPAPI_KEY = os.getenv('SERPAPI_KEY', '')

if not OPENAI_API_KEY:
    print("ERROR: OPENAI_API_KEY not found in environment")
    print("Please set it: export OPENAI_API_KEY='your-key-here'")
    exit(1)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Test output directory
TEST_DIR = Path('./test_output')
TEST_DIR.mkdir(exist_ok=True)

# ==================== SYSTEM PROMPT ====================
SYSTEM_GDOT = """You are an expert technical writer and educator for the Georgia Department of Transportation (GDOT).
Your audience includes DOT contractors, engineers, and technical staff.
Your goal is to simplify Bridge Design Manuals and technical documentation while maintaining safety and compliance standards.

Style Guidelines:
- Professional, clear, and concise language
- Focus on practical applications and real-world scenarios
- Emphasize safety and regulatory compliance
- Use technical terminology appropriately
- Break down complex concepts into digestible steps

Visual Guidelines:
- White or light backgrounds for professional appearance
- Clean, technical diagrams and charts
- High-contrast colors for visibility
- Professional fonts and layouts
- Focus on clarity and information density"""

# ==================== SAMPLE TEST CONTENT ====================
SAMPLE_MD = """# SECTION 3 SUPERSTRUCTURE

The superstructure of a bridge is that portion of the bridge above the caps. This includes the bearing devices, beams, decks, and railings.

# A. Check of Substructure

The location, both vertically and horizontally, of the substructure controls the location of the superstructure. The location of the substructure must be checked before superstructure construction is commenced. The Contractor must verify the elevations for all bearingseats before setting beams. Also, the centerline of each beam or girder shall be laid out and the location of the anchor bolt holes or dowel barschecked.

# B. Preparation of Bearing Areas

The areas of the cap where the bridge seats bear must be level and flat. These areas have been finished with a Type IV finish. A short (not over 6 inch) spirit level should be used to check these areas. If the areas are high in elevation or are not flat (either convex or concave) they must be ground down to a true surface. If the resulting area is low or started out low because of an error in elevation the lowness shall be compensated for by either shimming under the bearing plates or by adjusting the coping over the beams. If the error is greater than ½" it shall be corrected by shimming. This is for steel or prestressed concrete beams or girders.

C. Structural Steel Beams and Girders: (Section 501 SteelStructures)

# 1. Shear Connectors

Shear connectors extend out from the beams into the deck. Most of the time shear connectors will be welded to the beams in the shop. If the Engineer is in doubt about the acceptability of the shear connector welding or if the shear connectors are to be welded in the field contact the Inspection Services Branch of the OMAT for advice.

# 2. Erection of Beams

Beams shall be erected in accordance with the Specifications. All beams and girders must be preinspected at time of delivery as evidenced by GDT stamp on each member. No erection shall commence until approved erection drawings are on the job. Beams should be braced together as they are erected.

# 3. Bearings

If unbonded elastomeric pads are used on concrete, no preparation other than leveling of the bearing areas is required. A level but textured (floated) surface is best for these pads. If the pads are to be bonded to the cap concrete the bearing area must be ground smooth.

Self-lubricating plates, bushings or sliding plates fabricated from bronze material require special test reports. As the structural steel is shop inspected the Inspection Services Branch of the OMAT will inspect all these plates that pass through the fabricating shop. Inspected bronze plates will not be tagged or stamped accepted but will arrive on the project in shipments of GDT stamped primary steel members. If bronze plates do not arrive on the job in shipments which also include GDT stamped steel, they shall be considered as being uninspected. Notice by telephone should be given to the Inspection Service Branch of the OMAT when uninspected bronze plates are received on the project. All bronze plates must be physically inspected by the Engineer.

# 4. Inspection of Splices Connections

The Contractor is responsible for providing safe access to allow inspection of all splices and connections.

a. Bolted

All bolted splices and diaphragm connections shall be checked for torque. Calibration of torque wrenches must be done before bolted connections begin.

# b. Welded

All welding on Georgia DOT projects must be performed by GDOT certified welders. Welding for butt splices must be performed by specially certified welders and must be ultrasonically inspected. The Project Engineer is responsible for visual inspection of all fillet welds and should have a weld fillet gauge (available through OMAT) to check the size of fillet welds. The Inspection Services Branch of the OMAT will ultrasonically test all welding of butt splices. The Inspection Services Branch of OMAT should be notified at least three days in advance when welding of butt splices is required in order to schedule ultrasonic testing of the welds. They should also be contacted if there is any question on the acceptability of other welded connections of for other guidance. Prior to scheduling non-destructive testing of field butt welds the Project Engineer shall inspect each welded splice to ensure that the Contractor has done the following:

1) Completed welding on all splices.   

2) Removed all back-up strips and ground flush with parentmaterial.   

3) Removed all notch-effect in weld profile.   

4) Removed all torch marks, slag, weld splatter, etc.   

5) Dressed-up weld profile to acceptable workmanship and design.

The Inspection Services inspector will locate and mark all rejects and furnish a written report of the findings. The Engineer must be present when the rejects are located and marked. Record the results in the diary. After the rejected welds are repaired, they shall be inspected again."""

# ==================== HELPER FUNCTIONS ====================
def print_step(step_no, title):
    """Print step header"""
    print("\n" + "="*80)
    print(f"STEP {step_no}: {title}")
    print("="*80)

def print_success(message):
    """Print success message"""
    print(f"[SUCCESS] {message}")

def print_error(message):
    """Print error message"""
    print(f"[ERROR] {message}")

def print_info(message):
    """Print info message"""
    print(f"[INFO] {message}")

def call_llm(prompt, max_tokens=1500, temperature=0.3):
    """Call OpenAI API"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_GDOT},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        content = response.choices[0].message.content
        tokens = response.usage.total_tokens
        return content, tokens
    except Exception as e:
        print_error(f"LLM call failed: {e}")
        raise

