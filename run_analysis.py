
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from src.analyze import make_goal_windows


# 1. Dateien laden
project = Path(__file__).resolve().parent
results = project / "results"
results.mkdir(exist_ok=True)

df = pd.read_csv(
    project / "outputs" / "turkey_euro2024_sentiment.csv"
)

goals = pd.read_csv(
    project / "annotations" / "goal_events_manual.csv"
)


# 2. Torfenster berechnen
windows = make_goal_windows(df, goals)


# 3. Sentiment vor und nach jedem Tor
windows["phase"] = windows["relative_seconds"].apply(
    lambda x: "vorher" if x < 0 else "nachher"
)

comparison = (
    windows.groupby(["goal_id", "phase"])["sentiment_score"]
    .mean()
    .unstack()
)

comparison["veraenderung"] = (
    comparison["nachher"] - comparison["vorher"]
)

comparison.reset_index().to_csv(
    results / "sentiment_vorher_nachher_pro_tor.csv",
    index=False
)


# 4. Sentimentverlauf pro Minute
windows["minute_bin"] = (
    windows["relative_seconds"] // 60
).astype(int)

per_goal = (
    windows.groupby(["goal_id", "minute_bin"])["sentiment_score"]
    .mean()
    .reset_index()
)

trend = (
    per_goal.groupby("minute_bin")["sentiment_score"]
    .agg(["mean", "count"])
    .reindex(range(-5, 5))
)

trend.reset_index().to_csv(
    results / "sentimentverlauf_minuten.csv",
    index=False
)


# 5. Balkendiagramm
plt.figure(figsize=(10, 5))
plt.bar(comparison.index, comparison["veraenderung"])
plt.axhline(0, color="black", linewidth=1)

plt.xlabel("Tor-ID")
plt.ylabel("Sentimentveraenderung")
plt.title("Sentimentveraenderung vor und nach Torereignissen")
plt.xticks(comparison.index)
plt.tight_layout()

plt.savefig(
    results / "sentiment_veraenderung_pro_tor.png",
    dpi=200
)
plt.close()


# 6. Verlaufsgrafik
plt.figure(figsize=(10, 5))

plt.plot(
    trend.index + 0.5,
    trend["mean"],
    marker="o"
)

plt.axvline(0, color="red", linestyle="--", label="Tor")
plt.axhline(0, color="gray", linewidth=1)

plt.xlabel("Minuten relativ zum Tor")
plt.ylabel("Mittlerer Sentiment-Score")
plt.title("Sentimentverlauf im Umfeld von Torereignissen")
plt.xticks(range(-5, 6))
plt.legend()
plt.grid(axis="y", alpha=0.2)
plt.tight_layout()

plt.savefig(
    results / "sentiment_verlauf_torfenster.png",
    dpi=200
)
plt.close()


# 7. Kontrolle
print("Analyse erfolgreich abgeschlossen!")
print("Untersuchte Tore:", windows["goal_id"].nunique())
print("Segmentzuordnungen:", len(windows))
print("Ergebnisordner:", results)
