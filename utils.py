def sizeof_fmt(num, suffix="B"):
    for unit in ["", "K", "M", "G"]:
        if abs(num) < 1024:
            return f"{num:.2f}{unit}{suffix}"
        num /= 1024
    return f"{num:.2f}T{suffix}"

async def progress_bar(current, total, message):
    try:
        percent = current * 100 / total
        bar = "█" * int(percent / 10) + "░" * (10 - int(percent / 10))
        await message.edit_text(f"`{bar}` {percent:.1f}%\n{current//1024//1024}MB of {total//1024//1024}MB")
    except:
        pass
