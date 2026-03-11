


def summarize_text(text: str, max_length: int = 300) -> str:
    try:
        from backend.app.services.generator import AiVeterinarian
        gen = AiVeterinarian()
        prompt = f"Кратко суммаризируй следующий медицинский текст (не более {max_length} символов):\n\n{text}"
        state = gen.ask(prompt, {"role": "summarizer", "animal": ""}, {"messages": [], "summary": ""})
        return state["messages"][-1].content
    except Exception:
        return text[:max_length] + "..." if len(text) > max_length else text
