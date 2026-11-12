import os
import json
from openai import OpenAI

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "ai_config.txt")

def load_ai_config():
    """Reads the current AI provider settings from ai_config.txt."""
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_ai_config(config_data):
    """Writes updated AI provider settings back to ai_config.txt."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)

def get_active_client_and_model():
    """Initializes an OpenAI-compatible client for the currently selected provider."""
    config = load_ai_config()
    active_name = config["active_provider"]
    provider = config["providers"][active_name]

    client = OpenAI(
        base_url=provider["base_url"],
        api_key=provider["api_key"].strip()
    )
    return client, provider["model"].strip(), provider.get("delay_seconds", 0)

def get_agent_prompts():
    return {
        "Design Engineer": "You are a Design Engineer. Review product architecture and design intent. Assess functionality, geometry, interfaces, clearances. Identify weaknesses. Evaluate materials. Use first principles reasoning. Be specific.",
        "DFM Engineer": "You are a DFM Engineer. Evaluate manufacturability. Review machining, casting, forging, fabrication. Identify difficult features and unnecessary costs. Suggest practical modifications.",
        "Simulation Engineer": "You are a Simulation Engineer. Perform transparent, first-principles engineering calculations (stress, strain, thermal, fluid flow). Use appropriate equations, clearly state assumptions, show formulas, units, and intermediate calculations. Do NOT use CAD, FEA, CFD or commercial simulation software. Do not invent loads or properties not provided.",
        "Manufacturing Engineer": "You are a Manufacturing Engineer. Evaluate proposed manufacturing route, sequence, tooling, assembly, and feasibility. Identify bottlenecks, cycle times, process capabilities, and production risks.",
        "Testing and Validation Engineer": "You are a Testing and Validation Engineer. Develop a Design Verification Plan and Report (DVP&R) structure. Identify functional, environmental, endurance tests. Recommend test methods and acceptance criteria.",
        "DFMEA Engineer": "You are a DFMEA Engineer. Prepare a Design Failure Mode and Effects Analysis. Assess severity, occurrence, detection. Calculate Risk Priority Number (RPN) where appropriate. Recommend prevention controls.",
    }

def run_specialist_agent(agent_name, text_context, images_b64):
    client, model_name, _ = get_active_client_and_model()
    prompts = get_agent_prompts()
    system_prompt = prompts.get(agent_name, "You are a senior engineer.")

    content = [{"type": "text", "text": "ENGINEERING PROJECT DATA:\n" + text_context}]
    for b64 in images_b64[:3]:
        content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}})

    messages = [
        {
            "role": "system",
            "content": system_prompt
            + "\n\nCRITICAL RULES:\n- Never invent dimensions, materials, or loads.\n- Clearly label all findings as preliminary assessments requiring engineer approval.\n- Structure output logically with headings: Executive Summary, Observations, Technical Analysis, Risks, Recommendations, Missing Information.\n- Keep the entire response concise and under 650 words.",
        },
        {"role": "user", "content": content},
    ]

    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.2,
        max_tokens=900,
    )
    return response.choices[0].message.content

def run_chief_engineer(text_context, previous_results, images_b64):
    client, model_name, _ = get_active_client_and_model()
    system_prompt = (
        "You are the Chief Engineering Manager. Review the findings of the 6 specialists. "
        "Identify agreements and disagreements between them. Challenge unsupported assumptions. "
        "Resolve conflicting recommendations. Prioritize critical risks. Provide an overall design "
        "maturity assessment and recommend whether the design is ready for prototyping or requires "
        "further development. You must not blindly accept specialist findings. "
        "Keep your entire report concise and under 650 words."
    )

    specialist_text = ""
    for agent, result in previous_results.items():
        specialist_text += f"\n\n====================\n{agent} Report:\n{result}\n====================\n"

    content = [{"type": "text", "text": "USER PROJECT DATA:\n" + text_context + "\n\nSPECIALIST REPORTS TO REVIEW:\n" + specialist_text}]
    for b64 in images_b64[:3]:
        content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}})

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": content},
    ]
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.2,
        max_tokens=900,
    )
    return response.choices[0].message.content