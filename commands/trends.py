import typer
from commands import top, stats

app = typer.Typer()

app.command()(top.top_episodes)
app.command()(stats.show_stats)

if __name__ == "__main__":
    app()
