import json
import math
import asyncio
import anthropic
from tool_definitions import TOOLS
from tools import TOOL_MAP

client = anthropic.Anthropic()


class _SafeEncoder(json.JSONEncoder):
    """Convert NaN/Inf (from yfinance) to None so json.dumps never raises."""
    def iterencode(self, o, _one_shot=False):
        return super().iterencode(self._sanitize(o), _one_shot)

    def _sanitize(self, obj):
        if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
            return None
        if isinstance(obj, dict):
            return {k: self._sanitize(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._sanitize(v) for v in obj]
        return obj

SYSTEM_PROMPT = """Always respond in the same language the user is using. If the user writes in English, respond in English. If the user writes in Chinese, respond in Traditional Chinese (繁體中文).

Keep responses concise. Maximum 3-4 bullet points per section. No lengthy explanations unless the user specifically asks for more detail.

You are a helpful AI financial assistant. You can look up real-time stock quotes,
financial statements, risk metrics, and macroeconomic indicators like CPI and interest rates.

When users ask about stocks or markets, use the available tools to fetch live data before answering.
Present numbers clearly and provide context to help users understand what the data means.
Always mention the data date/period when relevant.

## Financial Statement Analysis Framework

When the user asks about financial statements or financial health, use the get_financials tool and interpret the data using the following CFA framework:

**Income Statement**
- Revenue Growth: Is growth accelerating or decelerating YoY?
- Gross Margin: Reflects pricing power and cost control
- Net Margin: Is it stable or improving? Watch for one-time items

**Balance Sheet**
- Debt-to-Equity: D/E > 2 signals elevated financial risk
- Current Ratio (Current Assets / Current Liabilities): < 1 indicates short-term liquidity pressure
- Asset mix: tangible vs. intangible assets; goodwill impairment risk

**Cash Flow Statement**
- Operating Cash Flow vs. Net Income: OCF consistently above net income = high earnings quality; if net income is high but OCF is low, watch for receivables bloat or inventory buildup
- Free Cash Flow (FCF = OCF - Capex): sustained positive FCF is the true measure of value creation

**Conclusion**
Always end with:
1. Financial health rating (Strong / Moderate / Weak) with reasoning
2. Key risk factors (e.g. high leverage, earnings quality concerns, deteriorating cash flow)
3. One key takeaway for investors"""


def _extract_text(content: list) -> str:
    for block in content:
        if hasattr(block, "text"):
            return block.text
    return ""


async def run_chat(messages: list) -> str:
    msgs = [{"role": m.role, "content": m.content} for m in messages]

    while True:
        response = await asyncio.to_thread(
            client.messages.create,
            model="claude-haiku-4-5-20251001",  # cheaper
            max_tokens=8192,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=msgs,
        )

        if response.stop_reason == "end_turn":
            return _extract_text(response.content)

        if response.stop_reason == "max_tokens":
            # Return whatever text Claude managed to produce
            return _extract_text(response.content) or "Response was too long. Please ask a more specific question."

        if response.stop_reason == "tool_use":
            msgs.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_fn = TOOL_MAP.get(block.name)
                    if tool_fn:
                        try:
                            result = tool_fn(**block.input)
                        except Exception as e:
                            result = {"error": str(e)}
                    else:
                        result = {"error": f"Unknown tool: {block.name}"}

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result, cls=_SafeEncoder),
                    })

            msgs.append({"role": "user", "content": tool_results})
        else:
            print(f"[run_chat] unexpected stop_reason: {response.stop_reason}")
            return _extract_text(response.content) or "Unexpected error. Please try again."
