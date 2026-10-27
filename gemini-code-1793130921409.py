import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(
    page_title="2002 Camry LE (2AZ-FE) 1,000,000-Mile Mod Studio",
    layout="wide",
    initial_sidebar_state="expanded"
)

PROFILE_FILE = "my_camry_build.json"


def render_svg(svg_raw: str) -> None:
    """
    Strips leading indentation and blank lines so CommonMark/Streamlit
    never misinterprets indented SVG tags as a <pre><code> code block.
    """
    clean_svg = "\n".join(line.strip() for line in svg_raw.splitlines() if line.strip())
    st.markdown(clean_svg, unsafe_allow_html=True)


# ==============================================================================
# 1. ENCYCLOPEDIC DATABASE: 2002 CAMRY LE 2.4L (2AZ-FE / U241E / NON-JBL)
# ==============================================================================
PARTS_DB = {
    "1. Million-Mile 2AZ-FE Engine Longevity": {
        "Existing Factory Stock 2AZ-FE Head Bolts & PCV": {
            "fitment": "Exact Fit (OEM 2.4L 2AZ-FE)",
            "diy_level": "Stock",
            "skills": [],
            "tools_needed": [],
            "lift_required": False,
            "longevity_pts": 0,
            "torque_specs": "Stock Head Bolts: 58 ft-lbs + 90° turn",
            "safety_warning": "2002-2006 2AZ-FE blocks are notorious for pulling the rear 3 cylinder head bolt threads out of the aluminum block around 150k-220k miles, causing coolant leaks.",
            "specs": "Factory torque-to-yield head bolts and standard crankcase ventilation.",
            "vendors": {"Existing Factory Stock": 0.00},
            "crutchfield_deps": []
        },
        "ARP 2AZ-FE Chromoly Head Stud Kit + Mishimoto Baffled Oil Catch Can": {
            "fitment": "Exact Fit (2.4L 2AZ-FE Block) + Universal Catch Can Bracket",
            "diy_level": "Master DIY (Precision Torque + Custom Catch Can Bracket)",
            "skills": ["Torque Angle Gauge", "Custom Bracket Fab"],
            "tools_needed": ["M11x1.5 Thread Chaser", "12-Point Deep Socket Set", "1/2\" Torque Wrench"],
            "lift_required": False,
            "longevity_pts": 20,
            "torque_specs": "ARP Studs: 65 ft-lbs in 3 equal steps w/ ARP Ultra-Torque lube | Valve Cover: 80 in-lbs",
            "safety_warning": "Clean block threads with an M11x1.5 thread chaser (never a cutting tap). If threads are already stripped, install a Time-Sert 2200 deep-thread insert kit first.",
            "specs": "ARP2000 8740 chromoly head studs permanently clamp the 2AZ-FE head against thermal warping. 50-micron bronze filter catch can prevents carbon buildup on piston oil control rings.",
            "vendors": {"MAPerformance": 359.00, "Amazon": 368.50, "Summit Racing": 374.95},
            "crutchfield_deps": [
                {"item": "Fel-Pro PermadryPlus Multi-Layer Steel (MLS) Head Gasket & Valve Cover Set", "price": 118.79, "source": "RockAuto", "reason": "Mandatory when upgrading head studs or resealing the top end."},
                {"item": "OEM Toyota 12204-28020 Metal PCV Valve + 4ft 3/8\" SAE J30R7 PCV Hose", "price": 24.50, "source": "Toyota OEM / AutoZone", "reason": "Plumbs the baffled catch can inline between the 2AZ-FE valve cover and intake manifold."},
                {"item": "Aisin WPT-801 OEM Water Pump & Idler Pulley", "price": 68.50, "source": "RockAuto", "reason": "Smart preventative replacement while working on the passenger side of the 2AZ-FE."}
            ]
        }
    },
    "2. U241E Transmission Cooling & Filtration": {
        "Existing Factory Stock Radiator Lower-Tank Cooler": {
            "fitment": "Exact Fit (OEM U241E 4-Speed Auto)",
            "diy_level": "Stock",
            "skills": [],
            "tools_needed": [],
            "lift_required": False,
            "longevity_pts": 0,
            "torque_specs": "Trans Drain Plug: 36 ft-lbs | Pan Bolts: 69 in-lbs",
            "safety_warning": "Stock ATF runs at 195-215°F in summer traffic. Heat is the #1 killer of U241E planetary gearsets and solenoids.",
            "specs": "Single-pass liquid-to-liquid heat exchanger inside the lower plastic radiator tank.",
            "vendors": {"Existing Factory Stock": 0.00},
            "crutchfield_deps": []
        },
        "Hayden 678 Stacked-Plate Aux Cooler + Magnefine Inline Filter": {
            "fitment": "Universal Fitment - Additional Hardware Needed",
            "diy_level": "Intermediate DIY (Plumbing + Custom Steel Mounting Straps)",
            "skills": ["Custom Bracket Fab"],
            "tools_needed": ["10mm Hex Drain Socket", "Hose Cutters", "Inch-Pound Torque Wrench"],
            "lift_required": False,
            "longevity_pts": 15,
            "torque_specs": "Hose Clamps: 25 in-lbs (Use smooth fuel-injection clamps, not worm-gear)",
            "safety_warning": "Plumb in series AFTER the stock radiator return line (driver-side lower nipple) so ATF warms up in winter but sheds excess heat before returning to the U241E pan.",
            "specs": "Drops U241E operating temps by 25-35°F (doubling fluid life). Magnefine inline filter captures microscopic clutch & ferrous wear down to 35 microns.",
            "vendors": {"RockAuto (Cooler + Filter)": 64.50, "Amazon": 72.00, "Summit Racing": 76.99},
            "crutchfield_deps": [
                {"item": "6 Feet of Gates 3/8\" ID SAE J1532 High-Temp Transmission Hose", "price": 22.00, "source": "RockAuto / NAPA", "reason": "Standard fuel line will sweat and crack when exposed to hot Type T-IV ATF."},
                {"item": "ABA Smooth-Band 3/8\" Fuel Injection Clamps (Pack of 10)", "price": 14.99, "source": "Amazon / McMaster-Carr", "reason": "Prevents slicing into rubber trans lines unlike perforated worm-gear clamps."},
                {"item": "4 Quarts Idemitsu ATF Type TLS (Toyota Type T-IV Equivalent) + Wix 58010 Pan Filter", "price": 54.00, "source": "RockAuto / Amazon", "reason": "Fresh U241E pan service + extra fluid capacity for the external cooler core."}
            ]
        }
    },
    "3. Alternator & High-Current Electrical": {
        "Existing Factory Stock 80A/100A Denso Alternator": {
            "fitment": "Exact Fit (OEM 2AZ-FE 4-Pin Oval Plug)",
            "diy_level": "Stock",
            "skills": [],
            "tools_needed": [],
            "lift_required": False,
            "longevity_pts": 0,
            "torque_specs": "14mm Pivot Bolt: 32 ft-lbs | 12mm Adjuster Lock Bolt: 14 ft-lbs",
            "safety_warning": "Disconnect negative battery terminal before touching the 10mm B+ stud. (Reman Denso 210-0466 replacement is $138.79 on RockAuto).",
            "specs": "80-100 Amps output. Factory 7-rib pulley.",
            "vendors": {"Existing Factory Stock": 0.00},
            "crutchfield_deps": []
        },
        "JS Alternators 250A High-Output (2AZ-FE) + 1/0 AWG 'Big 3'": {
            "fitment": "Direct Bolt-On to 2AZ-FE Bracket (Requires Shorter Belt & Big 3)",
            "diy_level": "Intermediate DIY (Heavy Lug Crimping / Torch Soldering)",
            "skills": ["Soldering"],
            "tools_needed": ["19mm Belt Tensioner Wrench", "Hydraulic Cable Lug Crimper / Butane Torch"],
            "lift_required": False,
            "longevity_pts": 5,
            "torque_specs": "14mm Mount: 32 ft-lbs | B+ Copper Stud Nut: 85 in-lbs (Do not over-torque brass stud!)",
            "safety_warning": "Stock 8-AWG charge wire WILL MELT under 250A load! You must crimp/solder 1/0 AWG OFC wire with a 250A ANL fuse within 12 inches of the positive battery post.",
            "specs": "250A peak / 165A idle output. Direct plug-and-play with 2002 Camry 2.4L 4-pin oval regulator plug. Uses smaller 1.75\" 7-rib overdrive pulley.",
            "vendors": {"JS Alternators": 399.00, "LibertyBassShop": 399.00},
            "crutchfield_deps": [
                {"item": "Sky High Car Audio 1/0 AWG OFC 'Big 3' Upgrade Kit w/ 250A ANL Fuse", "price": 89.95, "source": "Sky High Car Audio / Amazon", "reason": "Upgrades Alternator-to-Battery(+), Battery(-)-to-Chassis, and 2AZ-FE Block-to-Chassis grounds."},
                {"item": "Gates K070750 Micro-V 7-Rib Serpentine Belt (75.5\" vs 76.0\" Stock)", "price": 29.79, "source": "RockAuto", "reason": "0.5-inch shorter 7-rib belt required to prevent belt slip on the smaller overdrive alternator pulley."}
            ]
        }
    },
    "4. Big Brake Kits (BBK) & Stopping Power": {
        "Existing Factory Stock Single-Piston Front Calipers (275mm)": {
            "fitment": "Exact Fit (Clears 15\"+ Wheels)",
            "diy_level": "Stock",
            "skills": [],
            "tools_needed": [],
            "lift_required": False,
            "min_wheel_size": 15,
            "longevity_pts": 0,
            "torque_specs": "Caliper Bracket: 79 ft-lbs | Slide Pins: 25 ft-lbs | Lug Nuts: 76 ft-lbs",
            "safety_warning": "Never let calipers hang by rubber brake hoses.",
            "specs": "Single 60mm piston floating caliper with 275mm (10.8\") rotors.",
            "vendors": {"Existing Factory Stock": 0.00},
            "crutchfield_deps": []
        },
        "OEM+ Highlander / Camry SE V6 Dual-Piston Caliper BBK (296mm)": {
            "fitment": "Direct Bolt-On to XV30 Knuckle (Requires 16\"+ Wheels!)",
            "diy_level": "Intermediate DIY (Brake Bleeding + Line Swap)",
            "skills": ["Brake Bleeding"],
            "tools_needed": ["10mm Flare Nut Wrench", "17mm Socket", "Vacuum Brake Bleeder"],
            "lift_required": True,
            "min_wheel_size": 16,
            "longevity_pts": 5,
            "torque_specs": "Caliper Mounting Bracket to Knuckle: 79 ft-lbs | Banjo Bolt: 22 ft-lbs",
            "safety_warning": "WHEEL CLEARANCE WARNING: These dual-piston calipers WILL NOT clear factory 15-inch steel wheels! Minimum 16-inch wheels required. Bleed brakes in sequence: RR -> LF -> LR -> RF.",
            "specs": "Bolts 2001-2007 Toyota Highlander / 02-06 Camry V6 twin-piston (2x44mm) calipers directly to the 2.4L knuckle with StopTech slotted 296mm cryo-rotors and Akebono ProACT ceramic pads.",
            "vendors": {"RockAuto (Reman Calipers + StopTech Rotors/Pads)": 385.00, "Summit Racing": 430.00},
            "crutchfield_deps": [
                {"item": "Goodridge G-Stop Braided Stainless Steel Brake Line Kit (21152)", "price": 142.99, "source": "Summit Racing / Tire Rack", "reason": "Replaces 20+ year old ballooning rubber hoses with Teflon-lined braided stainless lines."},
                {"item": "1 Liter ATE TYP 200 Amber DOT 4 High-Temp Brake Fluid", "price": 21.99, "source": "Amazon / FCP Euro", "reason": "536°F dry boiling point fluid to flush old moisture-contaminated fluid."},
                {"item": "New Copper Banjo Crush Washers (Pack of 8)", "price": 6.50, "source": "AutoZone", "reason": "Never reuse crushed copper washers on brake caliper banjo fittings."}
            ]
        },
        "Ceika Custom 6-Piston Forged Big Brake Kit (330mmx28mm 2-Piece Rotors)": {
            "fitment": "Custom Built for XV30 Camry (Requires 17\"+ Wheels!)",
            "diy_level": "Advanced DIY / Lift Recommended",
            "skills": ["Brake Bleeding"],
            "tools_needed": ["10mm Flare Nut Wrench", "Dial Indicator (Rotor Runout)", "Tin Snips (Dust Shield Trim)"],
            "lift_required": True,
            "min_wheel_size": 17,
            "longevity_pts": 5,
            "torque_specs": "Radial Mount Bracket: 85 ft-lbs | Radial Stud Nuts: 65 ft-lbs | Lugs: 76 ft-lbs",
            "safety_warning": "WHEEL CLEARANCE WARNING: Requires minimum 17-inch wheels with spoke clearance (+35 to +40 offset recommended). Check rotor-to-dust-shield clearance and trim factory backing plate lip.",
            "specs": "Forged 6061-T6 6-piston calipers, 330mm (13\") slotted/drilled floating 2-piece rotors with aluminum hats, braided Teflon lines, and radial mounting brackets.",
            "vendors": {"Ceika Performance Direct": 1360.00},
            "crutchfield_deps": [
                {"item": "Motul RBF 600 Factory Line DOT 4 Brake Fluid (2 Bottles)", "price": 42.00, "source": "Amazon / Summit Racing", "reason": "High thermal capacity fluid for 6-piston calipers."},
                {"item": "3mm Billet 5x114.3 Hub-Centric Wheel Spacers (Optional Insurance)", "price": 34.99, "source": "Fitment Industries", "reason": "Ensures inner wheel spoke clearance over wide 6-piston caliper bodies."}
            ]
        }
    },
    "5. Polyurethane Bushings, Wheel Bearings & Chassis": {
        "Existing Factory Stock Rubber Bushings & Wheel Bearings": {
            "fitment": "Exact Fit (OEM XV30)",
            "diy_level": "Stock",
            "skills": [],
            "tools_needed": [],
            "lift_required": False,
            "longevity_pts": 0,
            "torque_specs": "Front Axle Nut: 217 ft-lbs",
            "safety_warning": "Factory rubber lower control arm vertical bushings tear and crack around 120k miles, causing wandering steering and uneven braking.",
            "specs": "Compliant voided rubber bushings and original sealed wheel bearings.",
            "vendors": {"Existing Factory Stock": 0.00},
            "crutchfield_deps": []
        },
        "SuperPro / PSB Polyurethane LCA & Sway Bushings + Koyo Wheel Bearings": {
            "fitment": "Exact Fit XV30 Chassis (Requires 20-Ton Hydraulic Press)",
            "diy_level": "Master DIY (Hydraulic Shop Press + Puller)",
            "skills": ["20-Ton Hydraulic Press", "Ball Joint Separator"],
            "tools_needed": ["20-Ton Shop Press", "30mm 12-Point Deep Axle Socket", "250 ft-lb Torque Wrench", "Snap Ring Pliers"],
            "lift_required": True,
            "longevity_pts": 10,
            "torque_specs": "Front LCA Horizontal Bolt: 103 ft-lbs | Rear Vertical Mount: 152 ft-lbs | 12-Pt Axle Nut: 217 ft-lbs",
            "safety_warning": "LIFT & PRESS WARNING: On the 2AZ-FE, the passenger front control arm bolt is blocked by the engine mount bracket. Unbolt the upper engine torque strut and slightly jack up the engine oil pan (using a wood block) by 1.5 inches to slide the bolt out. Pressing wheel bearings requires a 20-ton press!",
            "specs": "Lifetime-warrantied self-lubricating polyurethane Front Lower Control Arm (LCA) bushings, front/rear sway bar poly bushings, poly upper engine torque rod insert, and OEM Japanese Koyo DAC4282W-3CS79 front wheel bearings.",
            "vendors": {"PSB Bushings + RockAuto (Koyo Bearings)": 284.00, "Suspension.com + Summit": 310.00},
            "crutchfield_deps": [
                {"item": "Sankei 555 (Made in Japan) Front Lower Ball Joints (Left & Right)", "price": 78.50, "source": "RockAuto / NAPA", "reason": "Bolts directly to the bottom of the knuckle with 3 bolts—replace while control arms are out."},
                {"item": "Toyota OEM Front Wheel Hub Snap Rings & Axle Lock Nuts (Pair)", "price": 24.00, "source": "Toyota Parts Deal / RockAuto", "reason": "Old snap rings corrode inside the knuckle bore, and axle nuts must be staked fresh at 217 ft-lbs."},
                {"item": "Energy Suspension Formula 5 Prelube Silicone Bushing Grease (8oz Tub)", "price": 18.99, "source": "Amazon / Summit Racing", "reason": "Prevents polyurethane bushing squeaks for tens of thousands of miles."}
            ]
        }
    },
    "6. Projector Headlight Retrofits & Lighting": {
        "Existing Factory Stock 9006/9005 Halogen Headlights": {
            "fitment": "Exact Fit (OEM 02-04 Camry)",
            "diy_level": "Stock",
            "skills": [],
            "tools_needed": [],
            "lift_required": False,
            "longevity_pts": 0,
            "torque_specs": "10mm Headlight Bolts: 45 in-lbs",
            "safety_warning": "Never put cheap plug-and-play LED bulbs in stock halogen reflectors—they scatter glare into oncoming traffic and reduce down-road distance.",
            "specs": "Factory polycarbonate lens with 9006 low beam / 9005 high beam reflectors.",
            "vendors": {"Existing Factory Stock": 0.00},
            "crutchfield_deps": []
        },
        "Custom DIY Retrofit: Morimoto Bi-LED M-LED 2.0 Projectors in OEM Housings": {
            "fitment": "Universal Threaded-Shaft Projector Retrofit (Requires Oven Baking)",
            "diy_level": "Master DIY (Oven Lens Baking + Soldering + Cutoff Alignment)",
            "skills": ["Headlight Oven Baking", "Soldering", "Dremel Clearancing"],
            "tools_needed": ["Kitchen Oven (225°F)", "Nylon Pry Tools", "Dremel Rotary Tool", "60W Soldering Iron"],
            "lift_required": False,
            "longevity_pts": 0,
            "torque_specs": "Projector Threaded Shaft Lock Nut: 15 ft-lbs w/ Blue Loctite",
            "safety_warning": "BAKING INSTRUCTIONS: Remove all bulbs and screws first! Preheat kitchen oven to 225°F, turn oven OFF, place headlight on cardboard over a wood block for 10-12 minutes to soften factory butyl glue, then pry lens open cleanly.",
            "specs": "True razor-sharp Z-beam cutoff with integrated Bi-LED solenoid (gives you quad high beams alongside your stock 9005s). Outperforms modern luxury car headlights.",
            "vendors": {"The Retrofit Source (TRS)": 385.00, "Headlight Revolution": 395.00},
            "crutchfield_deps": [
                {"item": "Morimoto RetroRubber Butyl Headlight Sealant Roll", "price": 18.00, "source": "The Retrofit Source", "reason": "Guarantees a 100% waterproof, condensation-free reseal when baking the lenses back on."},
                {"item": "9006 Low-Beam + 9005 High-Beam Bi-LED Splitter Harnesses (Pair)", "price": 25.00, "source": "The Retrofit Source", "reason": "Triggers the projector high-beam shield solenoid whenever you flick your high beams."},
                {"item": "Apollo 2.0 Chrome/Black Projector Shrouds + Centric Rings", "price": 35.00, "source": "The Retrofit Source", "reason": "Gives the projector lens an OEM-factory finished appearance inside the Camry bowl."}
            ]
        },
        "Anzo / Spec-D Black-Housing Bolt-In Projector Headlight Assemblies": {
            "fitment": "Exact Fit (02-04 Camry XV30 Bolt-On)",
            "diy_level": "DIY Friendly (Front Bumper Top Clips + 10mm Socket)",
            "skills": [],
            "tools_needed": ["10mm Socket", "Plastic Clip Removal Tool"],
            "lift_required": False,
            "longevity_pts": 0,
            "torque_specs": "10mm Mounting Bolts: 45 in-lbs",
            "safety_warning": "Run a bead of clear silicone RTV around the outer plastic seam before installing—aftermarket housings have thin factory sealant that can fog up in rain.",
            "specs": "Pre-assembled black or chrome projector housings with LED halo rings. Direct plug-and-play without baking open your factory lights.",
            "vendors": {"Amazon": 189.00, "CarParts.com": 198.99, "Redline360": 215.00},
            "crutchfield_deps": [
                {"item": "Permatex Flowable Clear Windshield & Glass Silicone Sealer", "price": 9.99, "source": "AutoZone", "reason": "Wicks into the outer lens seam to permanently prevent moisture intrusion."},
                {"item": "Morimoto 2Stroke 4.0 H1/H7 LED Projector Bulbs", "price": 170.00, "source": "The Retrofit Source", "reason": "Upgrades the dim halogen bulbs included in pre-built aftermarket projectors."}
            ]
        }
    },
    "7. Exhaust, Headers & Custom Welding": {
        "Existing Factory Stock 2AZ-FE Manifold & Muffler": {
            "fitment": "Exact Fit (OEM 2AZ-FE)",
            "diy_level": "Stock",
            "skills": [],
            "tools_needed": [],
            "lift_required": False,
            "longevity_pts": 0,
            "torque_specs": "Manifold Nuts: 27 ft-lbs",
            "safety_warning": "None.",
            "specs": "Factory tubular/cast manifold and quiet steel exhaust.",
            "vendors": {"Existing Factory Stock": 0.00},
            "crutchfield_deps": []
        },
        "Custom TIG/MIG-Welded 2.25\" 304 Stainless Exhaust w/ Vibrant Resonator & V-Bands": {
            "fitment": "Custom Fabrication Required (Welded on Car)",
            "diy_level": "Master Fabricator (MIG/TIG Stainless Welding + Lift)",
            "skills": ["MIG/TIG Welding", "Exhaust Pipe Cutting/Fit-Up"],
            "tools_needed": ["TIG or MIG Welder w/ Argon Gas", "Angle Grinder / Band Saw", "Auto-Darkening Welding Helmet"],
            "lift_required": True,
            "longevity_pts": 5,
            "torque_specs": "V-Band Clamps: 90 in-lbs | Spring-Bolt Flange: 32 ft-lbs",
            "safety_warning": "WELDING SAFETY: Disconnect negative battery terminal AND unplug the 2AZ-FE ECM behind the glovebox before striking an arc on the chassis! Use ER308L filler wire with Argon shielding gas so welds never rust over 1,000,000 miles.",
            "specs": "Mandrel-bent 16-gauge 304 stainless steel 2.25\" piping from the cat back, featuring a Vibrant 1790 Bottle Style Resonator (eliminates 4-cylinder rasp), Vibrant 1146 StreetPower Flat Black Muffler, and quick-release stainless V-band clamps.",
            "vendors": {"Vibrant Performance / Ace Race Parts": 460.00, "Summit Racing (304SS Builder Kit)": 485.00},
            "crutchfield_deps": [
                {"item": "2.25\" 304 Stainless Interlocking Male/Female V-Band Clamp Assemblies (x2)", "price": 68.00, "source": "Ace Race Parts / Summit Racing", "reason": "Lets you drop the rear axle-back or mid-pipe in 2 minutes with zero leaking paper gaskets."},
                {"item": "Blue Demon ER308L .030\" Stainless MIG Wire (2 lb Spool) + 1/2\" 304SS Hanger Rods", "price": 38.50, "source": "Amazon / Local Welding Supply", "reason": "Correct stainless filler metal so your welds match the corrosion resistance of the 304SS tubing."},
                {"item": "OEM Toyota 17451-0D020 Graphite Donut Exhaust Flange Gasket", "price": 17.50, "source": "RockAuto", "reason": "Seals the front spring-bolt ball joint behind the catalytic converter."}
            ]
        }
    },
    "8. Non-JBL Audio & Soldering Workbench": {
        "Existing Factory Stock Non-JBL Radio & 6x9 Speakers": {
            "fitment": "Exact Fit (OEM Standard 6-Speaker Non-JBL)",
            "diy_level": "Stock",
            "skills": [],
            "tools_needed": [],
            "lift_required": False,
            "longevity_pts": 0,
            "torque_specs": "10mm Radio Bracket Bolts: 35 in-lbs",
            "safety_warning": "None.",
            "specs": "Factory non-amplified head unit driving dash tweeters, front 6x9s, and rear deck 6x9s.",
            "vendors": {"Existing Factory Stock": 0.00},
            "crutchfield_deps": []
        },
        "Sony XAV-AX4000 Wireless CarPlay + JBL Club 9632 6x9s (Soldered Harness Build)": {
            "fitment": "Exact Fit (2002 Camry Non-JBL Opening & Doors)",
            "diy_level": "Intermediate DIY (Bench Soldering + Heat Shrink + Door Cards)",
            "skills": ["Soldering"],
            "tools_needed": ["60W Temperature-Controlled Soldering Iron", "Heat Gun", "Wire Strippers", "10mm Deep Socket"],
            "lift_required": False,
            "longevity_pts": 0,
            "torque_specs": "Reuse Factory Steel Radio Side Brackets on Sony Chassis (8mm screws)",
            "safety_warning": "SOLDERING BEST PRACTICE: Twist stripped copper strands in a mechanical lineman's splice, heat the wire from underneath with a 60W iron, feed 60/40 rosin-core solder into the top of the copper (never acid-core plumbing solder!), and seal with adhesive-lined 3:1 heat shrink tubing.",
            "specs": "Wireless Apple CarPlay / Android Auto, LDAC Bluetooth, 14-band EQ, time alignment, plus high-sensitivity 3-ohm JBL 6x9 3-way speakers in front doors and rear deck.",
            "vendors": {"Best Buy / Amazon": 649.00, "Crutchfield (Head Unit + 2 Pairs 6x9s)": 675.90},
            "crutchfield_deps": [
                {"item": "Metra 70-1761 Wiring Harness (Standard Non-JBL 1987-2007 Toyota)", "price": 11.99, "source": "Crutchfield / Amazon", "reason": "Solder this to the Sony pigtail on your workbench so your factory Toyota dash plugs remain 100% uncut."},
                {"item": "Metra 95-8204 Double-DIN Dash Kit (02-06 Camry)", "price": 17.99, "source": "Crutchfield", "reason": "Fills the wider Toyota radio bezel trim opening cleanly."},
                {"item": "Metra 82-8146 Front 6x9 Adapter Plates + Metra 72-8104 Speaker Harnesses (2 Pairs)", "price": 45.97, "source": "Crutchfield", "reason": "Replaces the deep molded factory front speaker pods and plugs straight into Toyota door wiring."},
                {"item": "Kester 44 Rosin-Core 60/40 Solder + 3:1 Marine Heat-Shrink Assortment", "price": 24.50, "source": "Amazon / DigiKey", "reason": "Creates vibration-proof, zero-resistance joints that will outlast crimp caps over 1,000,000 miles."}
            ]
        }
    },
    "9. Suspension & Stance": {
        "Existing Factory Stock Struts & Coil Springs": {
            "fitment": "Exact Fit (02-06 Camry 2.4L)",
            "diy_level": "Stock",
            "skills": [],
            "tools_needed": [],
            "lift_required": False,
            "drop_range": (0.0, 0.0),
            "default_drop": 0.0,
            "longevity_pts": 0,
            "torque_specs": "Lower Knuckle-to-Strut Bolts: 155 ft-lbs | Upper Strut Tower Nuts: 59 ft-lbs",
            "safety_warning": "None when keeping existing struts intact.",
            "specs": "OEM ride height and factory damping calibrated for the 2.4L 2AZ-FE front end.",
            "vendors": {"Existing Factory Stock": 0.00},
            "crutchfield_deps": []
        },
        "KYB Excel-G OEM-Spec 4-Corner Strut & Mount Refresh (Stock Height)": {
            "fitment": "Exact Fit (02-06 Camry 2.4L)",
            "diy_level": "Advanced DIY (Clamshell Spring Compressor + Jack Stands)",
            "skills": ["Spring Compressor Safety"],
            "tools_needed": ["Clamshell Strut Spring Compressor", "22mm Knuckle Socket", "Breaker Bar"],
            "lift_required": True,
            "drop_range": (0.0, 0.0),
            "default_drop": 0.0,
            "longevity_pts": 5,
            "torque_specs": "Lower Knuckle-to-Strut Bolts: 155 ft-lbs | Upper Strut Tower Nuts: 59 ft-lbs",
            "safety_warning": "DANGER: Always use a heavy-duty clamshell compressor or buy pre-assembled KYB Strut-Plus units to avoid high-tension spring release.",
            "specs": "Restores brand-new factory damping and ride comfort for another 150,000+ miles.",
            "vendors": {"RockAuto (4x KYB Struts + Mounts)": 385.00, "Amazon": 415.00},
            "crutchfield_deps": [
                {"item": "KYB SM5423 / SM5424 Upper Strut Mounts & Bearings (Set of 4)", "price": 110.00, "source": "RockAuto", "reason": "Worn upper front strut bearings clunk when turning the steering wheel."}
            ]
        },
        "H&R Sport Lowering Springs (-1.4\" F / -1.3\" R) + KYB Struts": {
            "fitment": "Exact Fit (02-06 Camry XV30)",
            "diy_level": "Advanced DIY (Spring Compressor + Lift/Stands)",
            "skills": ["Spring Compressor Safety"],
            "tools_needed": ["Clamshell Strut Spring Compressor", "22mm Knuckle Socket", "Torque Wrench"],
            "lift_required": True,
            "drop_range": (1.2, 1.6),
            "default_drop": 1.4,
            "longevity_pts": 5,
            "torque_specs": "Knuckle-to-Strut Bolts: 155 ft-lbs | Top Hat Nuts (F): 59 ft-lbs, (R): 29 ft-lbs",
            "safety_warning": "LIFT & SPRING WARNING: Compress springs evenly and align the lower spring pigtail into the strut perch step.",
            "specs": "Progressive-rate German spring steel that lowers the XV30 ~1.4 inches while keeping daily-driver compliance.",
            "vendors": {"Tire Rack (H&R + KYB Package)": 615.00, "Fitment Industries": 635.00},
            "crutchfield_deps": [
                {"item": "SPC 81290 Front Camber Adjusting Bolts (Pair)", "price": 32.50, "source": "Summit Racing", "reason": "Provides +/- 1.75 degrees of camber adjustment after lowering."},
                {"item": "4-Wheel Laser Alignment", "price": 125.00, "source": "Local Alignment Shop", "reason": "Mandatory after lowering ride height."}
            ]
        },
        "BC Racing BR Series Coilovers (XV30 2.4L Spec: 8k Front / 6k Rear)": {
            "fitment": "Exact Fit (02-06 Camry XV30)",
            "diy_level": "Advanced DIY / Lift & Alignment Required",
            "skills": ["Suspension Corner Preload Setup"],
            "tools_needed": ["Coilover Spanner Wrenches", "22mm Socket", "Digital Caliper / Tape Measure"],
            "lift_required": True,
            "drop_range": (0.8, 3.0),
            "default_drop": 1.8,
            "longevity_pts": 5,
            "torque_specs": "Knuckle-to-Strut Bolts: 155 ft-lbs | Top Hat Nuts (F): 59 ft-lbs, (R): 29 ft-lbs",
            "safety_warning": "LIFT WARNING: Support vehicle on a 2-post lift or 4 rated jack stands. Remove the rear seat side bolsters to reach the three 12mm upper rear strut tower nuts cleanly.",
            "specs": "30-way adjustable mono-tube damping, independent ride height adjustment via lower mount (retains full shock stroke at any drop), front pillowball camber plates.",
            "vendors": {"Fitment Industries": 1195.00, "MAPerformance": 1195.00, "Redline360": 1195.00},
            "crutchfield_deps": [
                {"item": "Sankei 555 / Moog Greaseable Front & Rear Sway Bar End Links (Set of 4)", "price": 82.00, "source": "RockAuto", "reason": "Factory end-link hex sockets strip out during removal—install greaseable heavy-duty links."},
                {"item": "4-Wheel Laser Alignment", "price": 135.00, "source": "Local Alignment Shop", "reason": "Mandatory after lowering ride height."}
            ]
        }
    },
    "10. Wheels, Tires & Hub Fitment (5x114.3 / 60.1mm Bore)": {
        "Existing Factory Stock 15\" Steel Wheels w/ Hubcaps (205/65R15)": {
            "fitment": "Exact Fit (OEM 15x6.5J +45mm, 60.1mm Bore)",
            "diy_level": "Stock",
            "skills": [],
            "tools_needed": [],
            "lift_required": False,
            "wheel_diam": 15,
            "spoke_style": "steelie",
            "longevity_pts": 0,
            "torque_specs": "Lug Nuts: 76 ft-lbs in 5-point star pattern",
            "safety_warning": "15-inch steel wheels WILL NOT clear Highlander Dual-Piston or Ceika 6-Piston Big Brake Kits.",
            "specs": "Factory 15x6.5J steel wheels with high-profile 205/65R15 touring tires.",
            "vendors": {"Existing Factory Stock": 0.00},
            "crutchfield_deps": []
        },
        "OEM+ 16\" Camry SE / Solara Alloy Wheels w/ 215/60R16 Michelin Defender2": {
            "fitment": "Exact Fit (OEM 16x6.5J +45mm, 60.1mm Hub-Centric)",
            "diy_level": "DIY Friendly (Floor Jack + Torque Wrench)",
            "skills": [],
            "tools_needed": ["21mm Thin-Wall Lug Socket", "1/2\" Torque Wrench"],
            "lift_required": False,
            "wheel_diam": 16,
            "spoke_style": "oem5",
            "longevity_pts": 0,
            "torque_specs": "OEM Mag-Seat Washer Lug Nuts: 76 ft-lbs",
            "safety_warning": "Use Toyota OEM flat-washer shank lug nuts (not conical tuner nuts) on factory Toyota alloy wheels.",
            "specs": "Clears the Highlander/V6 296mm Dual-Piston Big Brake Kit while keeping an OEM+ sleeper look and 80,000-mile treadwear tires.",
            "vendors": {"Discount Tire + OEM Refurbished Alloys": 1080.00, "Tire Rack": 1120.00},
            "crutchfield_deps": [
                {"item": "Dorman 611-211 Toyota Mag-Seat Washer Lug Nuts (Set of 20)", "price": 44.00, "source": "RockAuto / AutoZone", "reason": "Factory steel-wheel acorn nuts do not properly seat on OEM Toyota aluminum alloys."}
            ]
        },
        "Enkei RPF1 17x8 +35mm (5x114.3) w/ 225/50R17 Continental DWS06+": {
            "fitment": "Aftermarket Fit (Requires Hub Centric Rings & Conical Lugs)",
            "diy_level": "DIY Friendly (Floor Jack + Torque Wrench)",
            "skills": [],
            "tools_needed": ["Tuner Spline/Thin-Wall Socket", "1/2\" Torque Wrench"],
            "lift_required": False,
            "wheel_diam": 17,
            "spoke_style": "rpf1",
            "longevity_pts": 0,
            "torque_specs": "Conical Acorn Lug Nuts: 76 ft-lbs (Re-torque after first 50 miles)",
            "safety_warning": "NEVER install conical-seat aftermarket wheels using flat-washer Toyota OEM lug nuts! Wheel studs can shear off.",
            "specs": "15.2 lbs ultra-lightweight flow-formed wheel. Clears both Highlander Dual-Piston and Ceika 330mm 6-Piston BBKs. +35mm offset sits flush with XV30 fenders.",
            "vendors": {"Tire Rack (Mounted & Balanced Package)": 1580.00, "Fitment Industries": 1610.00},
            "crutchfield_deps": [
                {"item": "73.1mm OD to 60.1mm ID Aluminum Hub Centric Rings (Set of 4)", "price": 19.99, "source": "Amazon / Enkei", "reason": "Prevents 65-mph steering wheel vibration by centering the 73.1mm Enkei bore on the 60.1mm Camry hub."},
                {"item": "Muteki SR48 M12x1.5 60-Degree Conical Tuner Lug Nuts (Set of 20)", "price": 65.00, "source": "Fitment Industries", "reason": "Mandatory 60-degree tapered seat lugs for aftermarket alloy wheels."}
            ]
        },
        "Konig Hypergram 18x8.5 +35mm (5x114.3) w/ 225/45R18 Michelin Pilot Sport AS4": {
            "fitment": "Aftermarket Aggressive Flush Fit (Requires Hub Rings & Conical Lugs)",
            "diy_level": "DIY Friendly (Floor Jack + Torque Wrench)",
            "skills": [],
            "tools_needed": ["Tuner Thin-Wall Socket", "1/2\" Torque Wrench"],
            "lift_required": False,
            "wheel_diam": 18,
            "spoke_style": "multi18",
            "longevity_pts": 0,
            "torque_specs": "Conical Acorn Lug Nuts: 76 ft-lbs",
            "safety_warning": "With 18x8.5 +35mm wheels and drops greater than 2.0 inches, check rear quarter-panel inner fender lip clearance under full compression.",
            "specs": "17.8 lbs flow-formed 12-spoke motorsport wheel. Maximum brake clearance for 330mm+ 6-piston rotors and crisp sidewall response.",
            "vendors": {"Fitment Industries (Mounted Package)": 1790.00, "Tire Rack": 1825.00},
            "crutchfield_deps": [
                {"item": "73.1mm OD to 60.1mm ID Aluminum Hub Centric Rings (Set of 4)", "price": 19.99, "source": "Amazon / Konig", "reason": "Centers the 73.1mm aftermarket wheel bore on the 60.1mm Toyota hub."},
                {"item": "Muteki SR48 M12x1.5 60-Degree Conical Tuner Lug Nuts (Set of 20)", "price": 65.00, "source": "Fitment Industries", "reason": "Mandatory conical seat lugs for aftermarket wheels."}
            ]
        }
    }
}

# ==============================================================================
# 2. SESSION STATE INITIALIZATION & SAVE/LOAD PROFILE LOGIC
# ==============================================================================
if "wheel_slider" not in st.session_state:
    st.session_state["wheel_slider"] = 15
if "drop_slider" not in st.session_state:
    st.session_state["drop_slider"] = 0.0
if "se_lip_chk" not in st.session_state:
    st.session_state["se_lip_chk"] = False

for cat_key, cat_dict in PARTS_DB.items():
    state_key = f"sel_{cat_key}"
    if state_key not in st.session_state:
        st.session_state[state_key] = list(cat_dict.keys())[0]


def sync_wheel_slider() -> None:
    cat_10 = "10. Wheels, Tires & Hub Fitment (5x114.3 / 60.1mm Bore)"
    chosen_pkg = st.session_state.get(f"sel_{cat_10}")
    if chosen_pkg and chosen_pkg in PARTS_DB[cat_10]:
        st.session_state["wheel_slider"] = PARTS_DB[cat_10][chosen_pkg]["wheel_diam"]


def sync_drop_slider() -> None:
    cat_9 = "9. Suspension & Stance"
    chosen_susp = st.session_state.get(f"sel_{cat_9}")
    if chosen_susp and chosen_susp in PARTS_DB[cat_9]:
        st.session_state["drop_slider"] = PARTS_DB[cat_9][chosen_susp]["default_drop"]


def load_stock_preset() -> None:
    for c_key, c_dict in PARTS_DB.items():
        st.session_state[f"sel_{c_key}"] = list(c_dict.keys())[0]
    st.session_state["wheel_slider"] = 15
    st.session_state["drop_slider"] = 0.0
    st.session_state["se_lip_chk"] = False


def load_million_mile_preset() -> None:
    master_picks = {
        "1. Million-Mile 2AZ-FE Engine Longevity": "ARP 2AZ-FE Chromoly Head Stud Kit + Mishimoto Baffled Oil Catch Can",
        "2. U241E Transmission Cooling & Filtration": "Hayden 678 Stacked-Plate Aux Cooler + Magnefine Inline Filter",
        "3. Alternator & High-Current Electrical": "JS Alternators 250A High-Output (2AZ-FE) + 1/0 AWG 'Big 3'",
        "4. Big Brake Kits (BBK) & Stopping Power": "OEM+ Highlander / Camry SE V6 Dual-Piston Caliper BBK (296mm)",
        "5. Polyurethane Bushings, Wheel Bearings & Chassis": "SuperPro / PSB Polyurethane LCA & Sway Bushings + Koyo Wheel Bearings",
        "6. Projector Headlight Retrofits & Lighting": "Custom DIY Retrofit: Morimoto Bi-LED M-LED 2.0 Projectors in OEM Housings",
        "7. Exhaust, Headers & Custom Welding": "Custom TIG/MIG-Welded 2.25\" 304 Stainless Exhaust w/ Vibrant Resonator & V-Bands",
        "8. Non-JBL Audio & Soldering Workbench": "Sony XAV-AX4000 Wireless CarPlay + JBL Club 9632 6x9s (Soldered Harness Build)",
        "9. Suspension & Stance": "BC Racing BR Series Coilovers (XV30 2.4L Spec: 8k Front / 6k Rear)",
        "10. Wheels, Tires & Hub Fitment (5x114.3 / 60.1mm Bore)": "Enkei RPF1 17x8 +35mm (5x114.3) w/ 225/50R17 Continental DWS06+"
    }
    for c_key, pick in master_picks.items():
        st.session_state[f"sel_{c_key}"] = pick
    st.session_state["wheel_slider"] = 17
    st.session_state["drop_slider"] = 1.8
    st.session_state["se_lip_chk"] = True


def save_build_profile(p_name: str, c_paint: str, tint: float, drop: float, wheel: int, se_l: bool, proj: bool) -> None:
    profile_data = {
        "paint_choice_name": p_name,
        "caliper_color": caliper_color,
        "tint_vlt": tint,
        "drop_inches": drop,
        "wheel_size": wheel,
        "se_lip": se_l,
        "projector_beam_on": proj,
        "selections": {c_key: st.session_state.get(f"sel_{c_key}") for c_key in PARTS_DB.keys()}
    }
    with open(PROFILE_FILE, "w") as f:
        json.dump(profile_data, f, indent=4)
    st.sidebar.success(f"💾 Build successfully saved to `{PROFILE_FILE}`!")


def load_build_profile() -> None:
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "r") as f:
            data = json.load(f)
        st.session_state["drop_slider"] = data.get("drop_inches", 0.0)
        st.session_state["wheel_slider"] = data.get("wheel_size", 15)
        st.session_state["se_lip_chk"] = data.get("se_lip", False)
        for c_key, sel_val in data.get("selections", {}).items():
            if f"sel_{c_key}" in st.session_state and sel_val in PARTS_DB[c_key]:
                st.session_state[f"sel_{c_key}"] = sel_val
        st.sidebar.success(f"📂 Build successfully loaded from `{PROFILE_FILE}`!")
        st.rerun()
    else:
        st.sidebar.warning(f"⚠️ No saved profile found at `{PROFILE_FILE}`. Save a build first!")


# ==============================================================================
# 3. SIDEBAR CONTROLS: GARAGE SAVE/LOAD, PRESETS & MOD DROPDOWNS
# ==============================================================================
st.sidebar.title("🛠️ 2AZ-FE 1,000,000-Mile Builder")
st.sidebar.markdown("**2002 Camry LE** | `2.4L 2AZ-FE` | `U241E 4AT` | `Non-JBL`")

# Visually Distinct Garage Save & Load Section
with st.sidebar.expander("💾 **Garage Build Profile (Save & Load)**", expanded=False):
    st.markdown("Persist your installed parts and visual setup locally to your garage profile.")
    sc1, sc2 = st.columns(2)
    with sc1:
        if st.button("💾 Save Build", use_container_width=True):
            save_build_profile(paint_choice[0], caliper_color, tint_vlt, drop_inches, wheel_size, se_lip, projector_beam_on)
    with sc2:
        if st.button("📂 Load Build", use_container_width=True):
            load_build_profile()

    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "r") as f:
            saved_json_str = f.read()
        st.download_button(
            label="⬇️ Export Profile JSON",
            data=saved_json_str,
            file_name=PROFILE_FILE,
            mime="application/json",
            use_container_width=True
        )

p_col1, p_col2 = st.sidebar.columns(2)
p_col1.button("🔄 Reset to Stock", on_click=load_stock_preset, use_container_width=True)
p_col2.button("🏆 1M-Mile Build", on_click=load_million_mile_preset, use_container_width=True)

with st.sidebar.expander("🎨 1. Exterior, Wheels & Brake Visuals", expanded=True):
    paint_choice = st.selectbox(
        "Paint / Wrap Color",
        options=[
            ("Lunar Mist Metallic (OEM 1C8)", "#C4C9CE"),
            ("Super White II (OEM 040)", "#F4F5F0"),
            ("Phantom Gray Pearl (OEM 1E3)", "#4E5257"),
            ("Catalina Blue Mica (OEM 8P4)", "#29466B"),
            ("Midnight Purple III (Custom Wrap)", "#331A38"),
            ("British Racing Green (Custom Paint)", "#0E3A2F")
        ],
        format_func=lambda x: x[0]
    )
    paint_color = paint_choice[1]

    caliper_color = st.selectbox(
        "Brake Caliper High-Temp Paint",
        options=[("Brembo Red", "#E52521"), ("TRD Gold / Bronze", "#D4AF37"), ("Acid Green", "#76FF03"), ("OEM Silver", "#A0AAB4")],
        format_func=lambda x: x[0]
    )[1]

    tint_vlt = st.slider("Window Tint VLT % (Lower = Darker)", 5, 70, 35, 5)
    drop_raw = st.slider("Ride Height Drop (Inches)", 0.0, 3.0, step=0.2, key="drop_slider")
    drop_inches = round(float(drop_raw), 1)
    wheel_size = int(st.slider("Visualizer Wheel Diameter (Inches)", 15, 19, step=1, key="wheel_slider"))
    se_lip = st.checkbox("Add XV30 SE Front Lip + Side Skirts", key="se_lip_chk")
    projector_beam_on = st.checkbox("Switch On Headlights (Preview Cutoff)", value=True)

st.sidebar.subheader("⚙️ 2. Select System Modifications")
selected_parts = {}
for category, items in PARTS_DB.items():
    cb = None
    if category.startswith("9."):
        cb = sync_drop_slider
    elif category.startswith("10."):
        cb = sync_wheel_slider

    choice = st.sidebar.selectbox(
        category,
        list(items.keys()),
        key=f"sel_{category}",
        on_change=cb
    )
    selected_parts[category] = (choice, items[choice])

# ==============================================================================
# 4. TELEMETRY, MILLION-MILE SCORE & FITMENT CONFLICT ENGINE
# ==============================================================================
base_longevity = 35
mod_longevity = sum(data["longevity_pts"] for _, data in selected_parts.values())
total_longevity = min(100, base_longevity + mod_longevity)

active_skills = sorted(list({skill for _, data in selected_parts.values() for skill in data["skills"]}))
active_tools = sorted(list({tool for _, data in selected_parts.values() for tool in data["tools_needed"]}))
lift_needed = any(data["lift_required"] for _, data in selected_parts.values())

bbk_name, bbk_data = selected_parts["4. Big Brake Kits (BBK) & Stopping Power"]
min_wheel_req = bbk_data.get("min_wheel_size", 15)

wheel_pkg_name, wheel_pkg_data = selected_parts["10. Wheels, Tires & Hub Fitment (5x114.3 / 60.1mm Bore)"]
pkg_wheel_diam = wheel_pkg_data.get("wheel_diam", 15)
spoke_style = wheel_pkg_data.get("spoke_style", "steelie")

susp_name, susp_data = selected_parts["9. Suspension & Stance"]
min_drop_ok, max_drop_ok = susp_data.get("drop_range", (0.0, 0.0))

has_arp_catch = "Existing Factory Stock" not in selected_parts["1. Million-Mile 2AZ-FE Engine Longevity"][0]
has_trans_cooler = "Existing Factory Stock" not in selected_parts["2. U241E Transmission Cooling & Filtration"][0]
has_ho_alt = "Existing Factory Stock" not in selected_parts["3. Alternator & High-Current Electrical"][0]
has_bbk = "Existing Factory Stock" not in bbk_name
is_6piston = "6-Piston" in bbk_name
has_poly_koyo = "Existing Factory Stock" not in selected_parts["5. Polyurethane Bushings, Wheel Bearings & Chassis"][0]
has_projectors = "Existing Factory Stock" not in selected_parts["6. Projector Headlight Retrofits & Lighting"][0]
has_welded_exhaust = "Existing Factory Stock" not in selected_parts["7. Exhaust, Headers & Custom Welding"][0]
has_soldered_audio = "Existing Factory Stock" not in selected_parts["8. Non-JBL Audio & Soldering Workbench"][0]
has_upgraded_susp = "Existing Factory Stock" not in susp_name

if has_ho_alt and has_arp_catch:
    eng_bay_callout = "⚡ 250A Alt + ARP Studs + Catch Can"
elif has_ho_alt:
    eng_bay_callout = "⚡ 250A High-Output Alt + Big 3"
elif has_arp_catch:
    eng_bay_callout = "★ ARP Head Studs + Oil Catch Can"
else:
    eng_bay_callout = ""

st.title("🚘 2002 Toyota Camry LE (2.4L 2AZ-FE) — 1,000,000-Mile Studio")

m1, m2, m3, m4 = st.columns(4)
m1.metric("1,000,000-Mile Longevity Score", f"{total_longevity} / 100", f"+{mod_longevity} pts from upgrades")
m2.metric("Stance & Wheel Spec", f'-{drop_inches:.1f}" Drop | {wheel_size}"', "5x114.3 / 60.1mm Bore")
m3.metric("Lift / Jack Stands Required?", "YES (Safety Lock)" if lift_needed else "No (Ground DIY)", delta_color="inverse" if lift_needed else "normal")
m4.metric("Custom Fabrication Skills", f"{len(active_skills)} Active", ", ".join(active_skills[:2]) if active_skills else "Basic Hand Tools")

if wheel_size < min_wheel_req or pkg_wheel_diam < min_wheel_req:
    st.error(
        f"🚨 **BRAKE-TO-WHEEL CLEARANCE CONFLICT:** You selected **{bbk_name}** (requires **{min_wheel_req}\"+** wheels), "
        f"but your Wheel Slider is at **{wheel_size}\"** and Category 10 Wheel Package is **{pkg_wheel_diam}\"**. "
        f"The caliper bridge will physically hit the inner wheel barrel! Select a **{min_wheel_req}\"+** wheel package in Category 10."
    )

if wheel_size != pkg_wheel_diam:
    st.info(
        f"ℹ️ **Custom Wheel Diameter Preview:** Your Visualizer Slider is previewing **{wheel_size}\"** wheels while Category 10 is set to **{wheel_pkg_name}** ({pkg_wheel_diam}\")."
    )

if not (round(min_drop_ok, 1) <= drop_inches <= round(max_drop_ok, 1)):
    st.warning(
        f"⚠️ **SUSPENSION DROP RANGE MISMATCH:** Your Ride Height Drop slider is at **-{drop_inches:.1f}\"**, "
        f"but **{susp_name}** is engineered for a **-{min_drop_ok:.1f}\" to -{max_drop_ok:.1f}\"** drop range. "
        f"{'Select H&R Sport Lowering Springs (-1.4\") or BC Racing Coilovers (-0.8\" to -3.0\") in Category 9.' if max_drop_ok == 0.0 else 'Select BC Racing Coilovers in Category 9 for full 0.8\" to 3.0\" height adjustability.'}"
    )

# ==============================================================================
# 5. MULTI-VIEW INTERACTIVE SVG X-RAY ENGINE (4 TABS)
# ==============================================================================
tab_ext, tab_eng, tab_under, tab_audio = st.tabs([
    "🚘 1. Exterior, Stance & BBK X-Ray",
    "⚙️ 2. 2AZ-FE Engine Bay & U241E Cooling",
    "🔧 3. Undercarriage, Poly Bushings & Welding",
    "🔊 4. Non-JBL Soldering & Audio Blueprint"
])

body_y = int(round(drop_inches * 10))
wheel_r = 27 + (wheel_size - 15) * 3
win_opacity = round(1.0 - (tint_vlt / 100.0), 2)
rotor_r = 22 if is_6piston else (19 if has_bbk else 14)


def render_wheel_spokes(cx: int, cy: int, r: int, style: str, w_size: int) -> str:
    if w_size == 15 and style == "steelie":
        return (
            f'<circle cx="{cx}" cy="{cy}" r="{r-5}" fill="#b0b8c1" fill-opacity="0.45" stroke="#8b949e" stroke-width="2" stroke-dasharray="6,4" />'
            f'<circle cx="{cx}" cy="{cy}" r="9" fill="#8b949e" stroke="#21262d" stroke-width="1.5" />'
        )
    elif style == "oem5" or w_size == 16:
        return (
            f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy-r}" stroke="#c9d1d9" stroke-width="4" />'
            f'<line x1="{cx}" y1="{cy}" x2="{cx+int(r*0.95)}" y2="{cy-int(r*0.31)}" stroke="#c9d1d9" stroke-width="4" />'
            f'<line x1="{cx}" y1="{cy}" x2="{cx+int(r*0.59)}" y2="{cy+int(r*0.81)}" stroke="#c9d1d9" stroke-width="4" />'
            f'<line x1="{cx}" y1="{cy}" x2="{cx-int(r*0.59)}" y2="{cy+int(r*0.81)}" stroke="#c9d1d9" stroke-width="4" />'
            f'<line x1="{cx}" y1="{cy}" x2="{cx-int(r*0.95)}" y2="{cy-int(r*0.31)}" stroke="#c9d1d9" stroke-width="4" />'
            f'<circle cx="{cx}" cy="{cy}" r="6" fill="#161b22" stroke="#58a6ff" stroke-width="1.5" />'
        )
    elif style == "multi18" or w_size >= 18:
        return (
            f'<line x1="{cx}" y1="{cy-r}" x2="{cx}" y2="{cy+r}" stroke="#c9d1d9" stroke-width="2" />'
            f'<line x1="{cx-r}" y1="{cy}" x2="{cx+r}" y2="{cy}" stroke="#c9d1d9" stroke-width="2" />'
            f'<line x1="{cx-int(r*0.71)}" y1="{cy-int(r*0.71)}" x2="{cx+int(r*0.71)}" y2="{cy+int(r*0.71)}" stroke="#c9d1d9" stroke-width="2" />'
            f'<line x1="{cx-int(r*0.71)}" y1="{cy+int(r*0.71)}" x2="{cx+int(r*0.71)}" y2="{cy-int(r*0.71)}" stroke="#c9d1d9" stroke-width="2" />'
            f'<circle cx="{cx}" cy="{cy}" r="7" fill="#161b22" stroke="#f0883e" stroke-width="1.5" />'
        )
    else:
        return (
            f'<line x1="{cx-3}" y1="{cy-r}" x2="{cx-3}" y2="{cy+r}" stroke="#c9d1d9" stroke-width="2" />'
            f'<line x1="{cx+3}" y1="{cy-r}" x2="{cx+3}" y2="{cy+r}" stroke="#c9d1d9" stroke-width="2" />'
            f'<line x1="{cx-int(r*0.86)}" y1="{cy-int(r*0.5)-2}" x2="{cx+int(r*0.86)}" y2="{cy+int(r*0.5)-2}" stroke="#c9d1d9" stroke-width="2" />'
            f'<line x1="{cx-int(r*0.86)}" y1="{cy-int(r*0.5)+2}" x2="{cx+int(r*0.86)}" y2="{cy+int(r*0.5)+2}" stroke="#c9d1d9" stroke-width="2" />'
            f'<line x1="{cx-int(r*0.86)}" y1="{cy+int(r*0.5)-2}" x2="{cx+int(r*0.86)}" y2="{cy-int(r*0.5)-2}" stroke="#c9d1d9" stroke-width="2" />'
            f'<line x1="{cx-int(r*0.86)}" y1="{cy+int(r*0.5)+2}" x2="{cx+int(r*0.86)}" y2="{cy-int(r*0.5)+2}" stroke="#c9d1d9" stroke-width="2" />'
            f'<circle cx="{cx}" cy="{cy}" r="7" fill="#161b22" stroke="#58a6ff" stroke-width="1.5" />'
        )


with tab_ext:
    svg_ext = f"""
    <svg viewBox="0 0 900 350" width="100%" height="340" xmlns="http://www.w3.org/2000/svg" style="background: linear-gradient(180deg, #0d1117 0%, #161b22 78%, #21262d 78%, #0d1117 100%); border-radius: 12px; border: 1px solid #30363d;">
      <line x1="0" y1="275" x2="900" y2="275" stroke="#484f58" stroke-width="3" />
      <g transform="translate(0, {body_y})">
        {f'<polygon points="105,172 0,168 0,245 105,184" fill="#58a6ff" fill-opacity="0.28" /><line x1="105" y1="172" x2="0" y2="168" stroke="#79c0ff" stroke-width="2.5" /><text x="12" y="160" fill="#79c0ff" font-size="11" font-family="sans-serif" font-weight="bold">Bi-LED Razor Z-Cutoff</text>' if (projector_beam_on and has_projectors) else (f'<polygon points="105,172 0,145 0,255 105,184" fill="#f2cc60" fill-opacity="0.18" />' if projector_beam_on else '')}
        <path d="M 115 218 L 105 176 Q 112 152 180 142 L 268 134 L 360 84 L 570 84 L 672 132 L 775 142 Q 795 155 790 212 L 730 220 L 115 218 Z" fill="{paint_color}" stroke="#0d1117" stroke-width="2.5" />
        {"<path d='M 98 212 L 150 212 L 150 224 L 95 224 Z' fill='#161b22' stroke='#58a6ff' stroke-width='1.5'/><rect x='290' y='215' width='300' height='7' fill='#161b22' stroke='#58a6ff' stroke-width='1'/>" if se_lip else ""}
        <path d="M 282 132 L 365 90 L 468 90 L 468 132 Z" fill="#8b949e" />
        <path d="M 478 90 L 562 90 L 652 132 L 478 132 Z" fill="#8b949e" />
        <path d="M 282 132 L 365 90 L 468 90 L 468 132 Z" fill="#050505" fill-opacity="{win_opacity}" />
        <path d="M 478 90 L 562 90 L 652 132 L 478 132 Z" fill="#050505" fill-opacity="{win_opacity}" />
        <polygon points="108,170 155,158 150,182 106,184" fill="{'#21262d' if has_projectors else '#e6edf3'}" stroke="#58a6ff" stroke-width="1.5" />
        {f'<circle cx="126" cy="172" r="7" fill="#79c0ff" stroke="#ffffff" stroke-width="1.5"/>' if has_projectors else ''}
        <polygon points="788,155 752,158 755,185 790,182" fill="#da3633" stroke="#ff7b72" stroke-width="1.5" />
        <circle cx="240" cy="215" r="46" fill="#0d1117" stroke="#21262d" stroke-width="2" />
        <circle cx="650" cy="215" r="46" fill="#0d1117" stroke="#21262d" stroke-width="2" />
        {f'<g><rect x="122" y="186" width="24" height="20" fill="#1f6feb" stroke="#79c0ff" stroke-width="2" rx="3"/><text x="35" y="126" fill="#79c0ff" font-size="11" font-family="sans-serif" font-weight="bold">❄ U241E Aux Cooler</text><line x1="134" y1="130" x2="134" y2="186" stroke="#79c0ff" stroke-dasharray="3,3"/></g>' if has_trans_cooler else ''}
        {f'<g><circle cx="182" cy="176" r="11" fill="#d29922" stroke="#f2cc60" stroke-width="2"/><text x="165" y="102" fill="#f2cc60" font-size="11" font-family="sans-serif" font-weight="bold">{eng_bay_callout}</text><line x1="182" y1="106" x2="182" y2="165" stroke="#f2cc60" stroke-dasharray="3,3"/></g>' if eng_bay_callout else ''}
        {f'<g><rect x="725" y="210" width="62" height="13" fill="#21262d" stroke="#f0883e" stroke-width="2" rx="4"/><text x="645" y="115" fill="#f0883e" font-size="11" font-family="sans-serif" font-weight="bold">🔥 TIG/MIG 304SS V-Band Exhaust</text><line x1="755" y1="120" x2="755" y2="210" stroke="#f0883e" stroke-dasharray="3,3"/></g>' if has_welded_exhaust else ''}
      </g>
      {f'<g><rect x="234" y="{172 + body_y}" width="12" height="{60 - body_y}" fill="#21262d" stroke="#f85149" stroke-width="2" rx="2"/><line x1="233" y1="{176 + body_y}" x2="247" y2="{194 + body_y}" stroke="#f2cc60" stroke-width="3" stroke-dasharray="4,3"/><rect x="644" y="{172 + body_y}" width="12" height="{60 - body_y}" fill="#21262d" stroke="#f85149" stroke-width="2" rx="2"/><line x1="643" y1="{176 + body_y}" x2="657" y2="{194 + body_y}" stroke="#f2cc60" stroke-width="3" stroke-dasharray="4,3"/><text x="295" y="66" fill="#f85149" font-size="11" font-family="sans-serif" font-weight="bold">🔴 Upgraded Strut / Coilover Assembly</text><line x1="290" y1="63" x2="246" y2="{176 + body_y}" stroke="#f85149" stroke-dasharray="3,3"/></g>' if has_upgraded_susp else ''}
      <circle cx="240" cy="235" r="41" fill="#161b22" stroke="#30363d" stroke-width="3" />
      <circle cx="240" cy="235" r="{wheel_r}" fill="#21262d" stroke="#c9d1d9" stroke-width="3" />
      <circle cx="240" cy="235" r="{rotor_r}" fill="#8b949e" stroke="#484f58" stroke-width="1.5" stroke-dasharray="{'4,2' if has_bbk else 'none'}" />
      <path d="M {240 - rotor_r - 3} 222 L {240 - rotor_r + 8} 220 L {240 - rotor_r + 8} {'246' if has_bbk else '236'} L {240 - rotor_r - 3} {'244' if has_bbk else '235'} Z" fill="{caliper_color}" stroke="#ffffff" stroke-width="1" />
      {render_wheel_spokes(240, 235, wheel_r, spoke_style, wheel_size)}
      <circle cx="650" cy="235" r="41" fill="#161b22" stroke="#30363d" stroke-width="3" />
      <circle cx="650" cy="235" r="{wheel_r}" fill="#21262d" stroke="#c9d1d9" stroke-width="3" />
      <circle cx="650" cy="235" r="15" fill="#8b949e" stroke="#484f58" stroke-width="1.5" />
      <rect x="632" y="224" width="8" height="14" fill="{caliper_color}" rx="2" />
      {render_wheel_spokes(650, 235, wheel_r, spoke_style, wheel_size)}
      <path d="M 194 {198 + body_y} Q 240 {142 + body_y} 286 {198 + body_y}" fill="none" stroke="{paint_color}" stroke-width="6" />
      <path d="M 604 {198 + body_y} Q 650 {142 + body_y} 696 {198 + body_y}" fill="none" stroke="{paint_color}" stroke-width="6" />
      <text x="20" y="28" fill="#e6edf3" font-size="13" font-family="monospace">
        XV30 Side X-Ray | Brakes: {"6-Piston 330mm" if is_6piston else ("Highlander Dual-Piston 296mm" if has_bbk else "Stock 275mm")} | Bushings: {"Polyurethane + Koyo" if has_poly_koyo else "Stock Rubber"}
      </text>
    </svg>
    """
    render_svg(svg_ext)

with tab_eng:
    svg_eng = f"""
    <svg viewBox="0 0 900 350" width="100%" height="340" xmlns="http://www.w3.org/2000/svg" style="background: #0d1117; border-radius: 12px; border: 1px solid #30363d;">
      <text x="20" y="28" fill="#58a6ff" font-size="14" font-family="monospace" font-weight="bold">
        TOP-DOWN ENGINE BAY SCHEMATIC: 2.4L 2AZ-FE (Transverse) + U241E 4-Speed Auto
      </text>
      <rect x="180" y="285" width="540" height="24" fill="#21262d" stroke="#8b949e" stroke-width="2" rx="4" />
      <text x="345" y="301" fill="#c9d1d9" font-size="12" font-family="sans-serif">OEM Radiator &amp; Lower Tank Heat Exchanger (Front of Car)</text>
      {f'<rect x="440" y="315" width="175" height="20" fill="#1f6feb" stroke="#79c0ff" stroke-width="2" rx="3" /><text x="452" y="329" fill="#ffffff" font-size="11" font-family="sans-serif" font-weight="bold">Hayden 678 Stacked-Plate Cooler</text><circle cx="635" cy="255" r="13" fill="#d29922" stroke="#f2cc60" stroke-width="2" /><text x="654" y="259" fill="#f2cc60" font-size="11" font-family="sans-serif" font-weight="bold">Magnefine 3/8" Magnetic Filter</text><path d="M 535 220 L 535 285 M 585 285 L 585 315 M 615 325 L 635 325 L 635 220" stroke="#ff7b72" stroke-width="3" fill="none" stroke-dasharray="5,3" />' if has_trans_cooler else '<text x="480" y="330" fill="#6e7681" font-size="11" font-family="sans-serif">[Select Aux Trans Cooler to view series plumbing]</text>'}
      <rect x="230" y="105" width="240" height="125" fill="#161b22" stroke="#8b949e" stroke-width="3" rx="8" />
      <text x="275" y="165" fill="#e6edf3" font-size="15" font-family="sans-serif" font-weight="bold">2.4L 2AZ-FE VVT-i</text>
      <text x="270" y="184" fill="#8b949e" font-size="11" font-family="sans-serif">Firing Order: 1-3-4-2 (Timing Chain Left)</text>
      {''.join([f'<circle cx="{255 + i*45}" cy="118" r="6" fill="{"#f85149" if has_arp_catch else "#484f58"}" stroke="#fff" stroke-width="1"/>' for i in range(5)])}
      {''.join([f'<circle cx="{255 + i*45}" cy="215" r="6" fill="{"#56d364" if has_arp_catch else "#484f58"}" stroke="#fff" stroke-width="1"/>' for i in range(5)])}
      {f'<text x="230" y="94" fill="#f85149" font-size="11" font-family="sans-serif" font-weight="bold">★ ARP 8740 Head Studs (Locks Rear Firewall Threads!)</text>' if has_arp_catch else ''}
      <rect x="140" y="120" width="85" height="24" fill="{'#79c0ff' if has_poly_koyo else '#30363d'}" stroke="#58a6ff" stroke-width="2" rx="6" />
      <text x="146" y="136" fill="#0d1117" font-size="10" font-family="sans-serif" font-weight="bold">{"Poly Torque Mount" if has_poly_koyo else "OEM Dogbone"}</text>
      {f'<circle cx="165" cy="200" r="22" fill="#238636" stroke="#56d364" stroke-width="2" /><text x="144" y="204" fill="#fff" font-size="10" font-family="sans-serif" font-weight="bold">Catch Can</text><path d="M 230 190 L 187 195 M 165 222 L 165 242 L 322 242 L 322 230" stroke="#56d364" stroke-width="2.5" fill="none" /><circle cx="322" cy="230" r="4" fill="#56d364" /><text x="285" y="256" fill="#56d364" font-size="10" font-family="sans-serif">PCV Clean Return</text>' if has_arp_catch else ''}
      <rect x="475" y="115" width="180" height="105" fill="#21262d" stroke="#58a6ff" stroke-width="2.5" rx="6" />
      <text x="500" y="165" fill="#79c0ff" font-size="14" font-family="sans-serif" font-weight="bold">U241E 4-Speed Auto</text>
      <text x="502" y="185" fill="#8b949e" font-size="11" font-family="sans-serif">Fluid: Toyota Type T-IV</text>
      <circle cx="255" cy="255" r="21" fill="{'#d29922' if has_ho_alt else '#30363d'}" stroke="#f2cc60" stroke-width="2" />
      <text x="235" y="259" fill="#fff" font-size="10" font-family="sans-serif" font-weight="bold">{"250A Alt" if has_ho_alt else "100A Alt"}</text>
      <rect x="700" y="120" width="125" height="75" fill="#161b22" stroke="#f85149" stroke-width="2" rx="4" />
      <text x="712" y="150" fill="#e6edf3" font-size="12" font-family="sans-serif" font-weight="bold">Group 35 Battery</text>
      <text x="712" y="170" fill="#8b949e" font-size="10" font-family="sans-serif">+250A ANL Fuse</text>
      {f'<path d="M 234 255 L 115 255 L 115 72 L 755 72 L 755 120" stroke="#f85149" stroke-width="3.5" fill="none" /><path d="M 825 155 L 865 155 M 230 160 L 95 160" stroke="#58a6ff" stroke-width="3" stroke-dasharray="4,2" fill="none" /><text x="455" y="64" fill="#ff7b72" font-size="11" font-family="sans-serif" font-weight="bold">1/0 AWG OFC "Big 3" Charge + Ground Leads (K070750 Belt)</text>' if has_ho_alt else ''}
    </svg>
    """
    render_svg(svg_eng)

with tab_under:
    svg_under = f"""
    <svg viewBox="0 0 900 350" width="100%" height="340" xmlns="http://www.w3.org/2000/svg" style="background: #0d1117; border-radius: 12px; border: 1px solid #30363d;">
      <text x="20" y="28" fill="#f0883e" font-size="14" font-family="monospace" font-weight="bold">
        UNDERCARRIAGE X-RAY: Polyurethane Bushings, Koyo Press Bearings, BBK &amp; Welded 304SS Exhaust
      </text>
      <rect x="170" y="95" width="110" height="160" fill="#161b22" stroke="#484f58" stroke-width="3" rx="8" />
      <text x="180" y="178" fill="#8b949e" font-size="10" font-family="sans-serif">XV30 Front Subframe</text>
      <path d="M 220 45 L 265 110 L 265 240 L 220 305" stroke="{'#58a6ff' if (has_poly_koyo or has_upgraded_susp) else '#6e7681'}" stroke-width="4" fill="none" />
      <rect x="258" y="120" width="14" height="16" fill="{'#1f6feb' if has_poly_koyo else '#484f58'}" stroke="#ffffff" stroke-width="1" rx="2" />
      <rect x="258" y="214" width="14" height="16" fill="{'#1f6feb' if has_poly_koyo else '#484f58'}" stroke="#ffffff" stroke-width="1" rx="2" />
      <polygon points="180,95 260,95 235,45 205,45" fill="#21262d" stroke="#8b949e" stroke-width="2" />
      <polygon points="180,255 260,255 235,305 205,305" fill="#21262d" stroke="#8b949e" stroke-width="2" />
      <circle cx="190" cy="95" r="9" fill="{'#1f6feb' if has_poly_koyo else '#484f58'}" stroke="#79c0ff" stroke-width="2" />
      <circle cx="252" cy="95" r="11" fill="{'#1f6feb' if has_poly_koyo else '#484f58'}" stroke="#79c0ff" stroke-width="2" />
      <circle cx="190" cy="255" r="9" fill="{'#1f6feb' if has_poly_koyo else '#484f58'}" stroke="#79c0ff" stroke-width="2" />
      <circle cx="252" cy="255" r="11" fill="{'#1f6feb' if has_poly_koyo else '#484f58'}" stroke="#79c0ff" stroke-width="2" />
      {f'<text x="280" y="92" fill="#79c0ff" font-size="11" font-family="sans-serif" font-weight="bold">◄ Polyurethane LCA &amp; Sway Bar Bushings</text>' if has_poly_koyo else ''}
      <rect x="195" y="25" width="50" height="22" fill="{'#238636' if has_poly_koyo else '#30363d'}" stroke="#56d364" stroke-width="2" rx="3" />
      <rect x="195" y="303" width="50" height="22" fill="{'#238636' if has_poly_koyo else '#30363d'}" stroke="#56d364" stroke-width="2" rx="3" />
      <text x="255" y="42" fill="#56d364" font-size="11" font-family="sans-serif" font-weight="bold">{"Koyo Press-In Bearings (217 ft-lbs) + 555 Ball Joints" if has_poly_koyo else "Stock Front Hubs &amp; Bearings"}</text>
      <rect x="165" y="22" width="24" height="14" fill="{caliper_color}" stroke="#fff" stroke-width="1.5" rx="2" />
      <rect x="165" y="314" width="24" height="14" fill="{caliper_color}" stroke="#fff" stroke-width="1.5" rx="2" />
      {f'<path d="M 177 36 L 177 95 M 177 314 L 177 255" stroke="#58a6ff" stroke-width="2.5" stroke-dasharray="3,2"/><text x="25" y="70" fill="#58a6ff" font-size="11" font-family="sans-serif" font-weight="bold">Goodridge Braided SS Lines</text>' if has_bbk else ''}
      <path d="M 280 175 L 780 175" stroke="{'#f0883e' if has_welded_exhaust else '#6e7681'}" stroke-width="10" fill="none" />
      <rect x="315" y="162" width="65" height="26" fill="#30363d" stroke="#8b949e" stroke-width="2" rx="6" />
      <text x="325" y="179" fill="#c9d1d9" font-size="10" font-family="sans-serif">OEM Cat</text>
      {f'<rect x="415" y="158" width="10" height="34" fill="#58a6ff" stroke="#ffffff" stroke-width="1.5" rx="2" /><text x="395" y="148" fill="#79c0ff" font-size="11" font-family="sans-serif" font-weight="bold">TIG V-Band #1</text><rect x="465" y="160" width="110" height="30" fill="#d29922" stroke="#f2cc60" stroke-width="2" rx="10" /><text x="475" y="179" fill="#0d1117" font-size="11" font-family="sans-serif" font-weight="bold">Vibrant 1790 Resonator</text><rect x="625" y="158" width="10" height="34" fill="#58a6ff" stroke="#ffffff" stroke-width="1.5" rx="2" /><text x="605" y="148" fill="#79c0ff" font-size="11" font-family="sans-serif" font-weight="bold">TIG V-Band #2</text><rect x="705" y="152" width="95" height="46" fill="#161b22" stroke="#f0883e" stroke-width="2.5" rx="6" /><text x="715" y="179" fill="#f0883e" font-size="11" font-family="sans-serif" font-weight="bold">Vibrant 304SS</text>' if has_welded_exhaust else '<text x="450" y="210" fill="#8b949e" font-size="12" font-family="sans-serif">[Select Custom TIG/MIG 304SS Exhaust to view V-Band &amp; Resonator Layout]</text>'}
    </svg>
    """
    render_svg(svg_under)

with tab_audio:
    svg_audio = f"""
    <svg viewBox="0 0 900 350" width="100%" height="340" xmlns="http://www.w3.org/2000/svg" style="background: #0d1117; border-radius: 12px; border: 1px solid #30363d;">
      <text x="20" y="28" fill="#56d364" font-size="14" font-family="monospace" font-weight="bold">
        {"NON-JBL SOLDERING WORKBENCH &amp; EIA HARNESS MAP (Metra 70-1761 Active)" if has_soldered_audio else "FACTORY STOCK NON-JBL 6-SPEAKER WIRING LAYOUT (Select Audio Upgrade to View Soldering Map)"}
      </text>
      <rect x="40" y="65" width="210" height="230" fill="#161b22" stroke="{'#58a6ff' if has_soldered_audio else '#484f58'}" stroke-width="2.5" rx="8" />
      <text x="58" y="95" fill="{'#79c0ff' if has_soldered_audio else '#c9d1d9'}" font-size="14" font-family="sans-serif" font-weight="bold">{"Sony XAV-AX4000" if has_soldered_audio else "Stock Non-JBL Radio"}</text>
      <text x="58" y="115" fill="#8b949e" font-size="11" font-family="sans-serif">{"Metra 95-8204 Dash Kit" if has_soldered_audio else "OEM Double-DIN Bezel"}</text>
      <rect x="55" y="130" width="180" height="105" fill="#0d1117" stroke="#30363d" rx="4" />
      <text x="68" y="185" fill="{'#56d364' if has_soldered_audio else '#8b949e'}" font-size="12" font-family="monospace">{"CarPlay / LDAC Active" if has_soldered_audio else "OEM CD / Cassette"}</text>
      <rect x="330" y="65" width="230" height="245" fill="#161b22" stroke="{'#d29922' if has_soldered_audio else '#484f58'}" stroke-width="2" stroke-dasharray="5,3" rx="8" />
      <text x="345" y="88" fill="{'#f2cc60' if has_soldered_audio else '#8b949e'}" font-size="12" font-family="sans-serif" font-weight="bold">{"🔥 60/40 Rosin Solder + Heat Shrink" if has_soldered_audio else "Plugged Directly Into OEM Loom"}</text>
      <line x1="250" y1="115" x2="640" y2="115" stroke="#f2cc60" stroke-width="3" />
      <text x="345" y="110" fill="#f2cc60" font-size="11" font-family="monospace">Yellow: 12V Constant (+B)</text>
      <line x1="250" y1="145" x2="640" y2="145" stroke="#f85149" stroke-width="3" />
      <text x="345" y="140" fill="#ff7b72" font-size="11" font-family="monospace">Red: 12V Ignition (ACC)</text>
      <line x1="250" y1="175" x2="640" y2="175" stroke="#8b949e" stroke-width="3" />
      <text x="345" y="170" fill="#c9d1d9" font-size="11" font-family="monospace">Black: Chassis Ground (-)</text>
      <line x1="250" y1="205" x2="640" y2="205" stroke="#58a6ff" stroke-width="3" />
      <text x="345" y="200" fill="#79c0ff" font-size="11" font-family="monospace">Blue/Wht: Amp Turn-On / Ant</text>
      <line x1="250" y1="235" x2="640" y2="235" stroke="#ffffff" stroke-width="3" />
      <text x="345" y="230" fill="#ffffff" font-size="11" font-family="monospace">Wht &amp; Gray: Front 6x9s (+/-)</text>
      <line x1="250" y1="265" x2="640" y2="265" stroke="#56d364" stroke-width="3" />
      <text x="345" y="260" fill="#56d364" font-size="11" font-family="monospace">Grn &amp; Violet: Rear 6x9s (+/-)</text>
      <rect x="640" y="65" width="225" height="230" fill="#21262d" stroke="{'#56d364' if has_soldered_audio else '#484f58'}" stroke-width="2.5" rx="8" />
      <text x="655" y="95" fill="{'#56d364' if has_soldered_audio else '#c9d1d9'}" font-size="13" font-family="sans-serif" font-weight="bold">{"Metra 70-1761 -&gt; Factory Plugs" if has_soldered_audio else "OEM 10-Pin &amp; 6-Pin Plugs"}</text>
      <text x="655" y="120" fill="#c9d1d9" font-size="11" font-family="sans-serif">{"• Zero Cut Factory Toyota Wires!" if has_soldered_audio else "• Unmodified Factory Loom"}</text>
      <text x="655" y="150" fill="#c9d1d9" font-size="11" font-family="sans-serif">{"• Front Doors: JBL 9632 6x9s" if has_soldered_audio else "• Front Doors: OEM Paper 6x9s"}</text>
      <text x="665" y="168" fill="#8b949e" font-size="10" font-family="sans-serif">{"(Metra 82-8146 + 72-8104 Adapters)" if has_soldered_audio else "(Molded 1-Piece Plastic Pods)"}</text>
      <text x="655" y="200" fill="#c9d1d9" font-size="11" font-family="sans-serif">{"• Rear Deck: JBL 9632 6x9s" if has_soldered_audio else "• Rear Deck: OEM Paper 6x9s"}</text>
      <text x="665" y="218" fill="#8b949e" font-size="10" font-family="sans-serif">{"(Metra 72-8104 Plug Adapters)" if has_soldered_audio else "(Factory Rear Parcel Shelf)"}</text>
      <text x="655" y="255" fill="#f2cc60" font-size="11" font-family="sans-serif">• Dash Tweeters wired in parallel</text>
    </svg>
    """
    render_svg(svg_audio)

# ==============================================================================
# 6. ENCYCLOPEDIC SPECS, TORQUE SPECS, CRUTCHFIELD DEPENDENCIES & CSV EXPORT
# ==============================================================================
col_left, col_right = st.columns([1.2, 1])

total_parts_min = 0.0
all_dependencies = []
export_rows = []

with col_left:
    st.subheader("📋 Encyclopedic Parts List, Torque Specs & Safety Protocols")
    for cat, (part_name, data) in selected_parts.items():
        is_upgraded = "Existing Factory Stock" not in part_name
        with st.expander(f"**{cat}:** {part_name} — *({data['fitment']})*", expanded=is_upgraded):
            st.markdown(f"**Engineering & Longevity Specs:** {data['specs']}")
            st.markdown(f"**Factory / Upgrade Torque Specs:** `{data['torque_specs']}`")
            st.markdown(f"**Install Complexity:** `{data['diy_level']}` | **1,000,000-Mile Bonus:** `+{data['longevity_pts']} pts`")

            if data["skills"]:
                st.markdown("**Fabrication / Shop Skills Used:** " + " ".join([f"`🛠️ {s}`" for s in data["skills"]]))
            if data["tools_needed"]:
                st.markdown("**Specialized Tools Required:** " + " ".join([f"`🧰 {t}`" for t in data["tools_needed"]]))

            if data["lift_required"]:
                st.error(f"🛑 **LIFT / PRESS / SAFETY WARNING:** {data['safety_warning']}")
            elif data["safety_warning"] != "None.":
                st.warning(f"⚠️ **Technical & Safety Note:** {data['safety_warning']}")

            v_df = pd.DataFrame(
                [(vendor, f"${price:,.2f}") for vendor, price in data["vendors"].items()],
                columns=["Vendor Website", "Price (USD)"]
            )
            st.dataframe(v_df, hide_index=True, use_container_width=True)

            min_price = min(data["vendors"].values())
            best_vendor = min(data["vendors"], key=data["vendors"].get)
            total_parts_min += min_price

            if is_upgraded:
                export_rows.append({
                    "Type": "Primary Upgrade",
                    "Category": cat,
                    "Item": part_name,
                    "Fitment": data["fitment"],
                    "Best Vendor": best_vendor,
                    "Price_USD": round(min_price, 2),
                    "Torque / Install Notes": data["torque_specs"]
                })

            for dep in data["crutchfield_deps"]:
                all_dependencies.append({"Category": cat, **dep})
                export_rows.append({
                    "Type": "Crutchfield Required Add-On",
                    "Category": cat,
                    "Item": dep["item"],
                    "Fitment": "Required Supporting Hardware",
                    "Best Vendor": dep["source"],
                    "Price_USD": round(dep["price"], 2),
                    "Torque / Install Notes": dep["reason"]
                })

with col_right:
    st.subheader("🔌 Crutchfield-Style Required Add-Ons & Shop Tool List")
    st.caption("Automatically populated based on your 2002 Camry LE 2.4L (2AZ-FE / U241E / Non-JBL) configuration.")

    if active_tools:
        with st.expander(f"🧰 **Master Specialized Tool Checklist ({len(active_tools)} Tools Required)**", expanded=True):
            st.markdown("\n".join([f"- **{t}**" for t in active_tools]))

    dep_total = 0.0
    if all_dependencies:
        for dep in all_dependencies:
            st.info(
                f"**{dep['Category']} Add-On:** {dep['item']} (**${dep['price']:.2f}** @ *{dep['source']}*)\n\n"
                f"👉 *Why it's required:* {dep['reason']}"
            )
            dep_total += dep["price"]
    else:
        st.success("✅ All currently selected components are Factory Stock ($0.00).")

    st.divider()
    grand_total = total_parts_min + dep_total
    st.metric("Total Build Cost (Lowest Vendor Prices + All Required Hardware)", f"${grand_total:,.2f}")

    if export_rows:
        export_rows.append({
            "Type": "SUMMARY",
            "Category": f"Longevity Score: {total_longevity}/100",
            "Item": f"BUILD GRAND TOTAL ({paint_choice[0]}, -{drop_inches:.1f}\" Drop, {wheel_size}\" Wheels)",
            "Fitment": "Complete Build",
            "Best Vendor": "Multiple Vendors",
            "Price_USD": round(grand_total, 2),
            "Torque / Install Notes": f"Lift Required: {'YES' if lift_needed else 'NO'}"
        })
        export_df = pd.DataFrame(export_rows)
        csv_bytes = export_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Complete 1,000,000-Mile Build Sheet & Torque Spec Checklist (CSV)",
            data=csv_bytes,
            file_name="2002_Camry_LE_2AZFE_Million_Mile_Build.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.caption("Select at least one upgrade in the sidebar to enable the CSV Build Sheet export.")