async def safe_edit(message, text=None, markup=None):
    try:
        if message.caption is not None: await message.edit_caption(caption=text, reply_markup=markup)
        else: await message.edit_text(text, reply_markup=markup)
    except Exception as e: print(f"Edit error: {e}")
