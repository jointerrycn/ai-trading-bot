import mplfinance as mpf

def save_chart(df, filename="chart.png"):
    df_plot = df.copy()
    df_plot.index = df_plot["time"]

    mpf.plot(
        df_plot,
        type="candle",
        style="charles",
        savefig=filename
    )

    return filename