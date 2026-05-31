import os
from google import genai

PROMPT_TEMPLATE= """
You are analyzing a broken AI session to build or improve
the user's personal AI guidelines file.

This could be any kind of session — coding, research,
learning, job hunting, planning, anything.

You will receive:
1. The broken session transcript
2. Their existing guidelines file — or NONE if they don't have one

If guidelines file is NONE:
- Output the four base instructions first exactly as written
  including all sub-bullets and context
- Then add 2-3 instructions specific to this session and
  this user's communication style

If guidelines file exists:
- Read every existing instruction carefully
- If the failure is an edge case of an existing instruction
  sharpen that instruction instead of adding a new one
- Never add a new instruction that overlaps with an existing one
- Only add what is genuinely missing
- Maximum 3 new or sharpened instructions per run
  fewer is fine
- If failure cannot be fixed with instructions say so
  in one sentence and add nothing

For every new instruction identify which type it is:
[behavior] — fixes something the AI did wrong
[style] — teaches the AI how this specific user thinks
and communicates so it interprets them correctly

Rules:
- Each instruction covers exactly one idea
- If two different problems were found write two separate
  instructions never combine them into one sentence
- If an instruction needs context or examples add sub-bullets
  below it exactly like the base instructions above
- An instruction with sub-bullets that actually works beats
  a single vague line that does not
- Maximum 3 outputs per run, fewer is fine
- If failure cannot be fixed with instructions say so
  in one sentence and add nothing
- No preamble, no explanation, no markdown

Output exactly this format and nothing else:

WHAT WENT WRONG: one sentence

BASE: (only output this section if guidelines file was NONE)
## 1. Think Before Responding
Don't assume. Don't hide confusion. Surface tradeoffs.
Before responding:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First
Minimum response that solves the problem. Nothing speculative.
- No scope beyond what was asked.
- No abstractions or extra steps that weren't requested.
- No flexibility or configurability that wasn't requested.
- If you can solve it in three sentences don't write ten.

## 3. Surgical Scope
Address only what was asked. Clean up only your own mess.
- Don't improve adjacent things that weren't mentioned.
- Don't refactor or restructure things that aren't broken.
- Match the user's existing direction even if you'd do it differently.
- If you notice something unrelated that needs fixing mention it
  but don't act on it unless asked.

## 4. Goal Driven
Confirm what success looks like before starting.
- Transform vague requests into verifiable goals before acting.
- For multi-step tasks state a brief plan and confirm before executing.
- If you hit a constraint or dead end say so immediately
  don't keep going and deliver something that misses the mark.
- Strong success criteria let you work independently.
  Weak criteria require constant clarification.

Credit: adapted from github.com/multica-ai/andrej-karpathy-skills

NEW:
[behavior] instruction
- sub-bullet if needed

[style] instruction
- sub-bullet if needed

SHARPEN: (only output this section if something needs sharpening)
[old instruction] → [sharpened version]
- sub-bullet if needed

SESSION:
{session_text}

GUIDELINES FILE:
{guidelines}
"""

# TODO: setup command will handle key naming properly
# for now we check standard names only
# KINTSUGI_GEMINI_API_KEY is ours, others are industry standard
def get_api_key():
    if os.environ.get("KINTSUGI_GEMINI_API_KEY"):
        return ("gemini", os.environ.get("KINTSUGI_GEMINI_API_KEY"))
    if os.environ.get("ANTHROPIC_API_KEY"):
        return ("anthropic", os.environ.get("ANTHROPIC_API_KEY"))
    if os.environ.get("OPENAI_API_KEY"):
        return ("openai", os.environ.get("OPENAI_API_KEY"))
    return None
def build_prompt(session_text, guidelines="NONE"):
    return PROMPT_TEMPLATE.format(session_text=session_text, guidelines=guidelines)
def diagnose(session_text, guidelines="NONE"):
    result = get_api_key()
    if result is None:
        raise Exception("No API key found. Set KINTSUGI_GEMINI_API_KEY, ANTHROPIC_API_KEY, or OPENAI_API_KEY in your environment.")
    
    provider, key = result
    prompt = build_prompt(session_text, guidelines)
    client = genai.Client(api_key=key)
    if provider == "gemini":
        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt
        )
        return response.text
    else:
        raise Exception("Only Gemini supported right now. Set KINTSUGI_GEMINI_API_KEY to continue.")
if __name__ == "__main__":
    with open("test_session.txt", "r") as f:
        session_text = f.read()
        
    # Call the function and print the result
    result = diagnose(session_text)
    print(result)