from matplotlib import pyplot as plt


def plot_intensity_data(channels_lines, times, metadata, show_plot=True):
    fig, ax = plt.subplots()
    ax.set_xlabel(f"Time (s, Laser period = {metadata['laser_period_ns']} ns)")
    ax.set_ylabel("Intensity (counts)")
    ax.set_title(
      "Intensity Tracing"
    )
    # plot all channels data
    for i in range(len(metadata["channels"])):
        channel_line = channels_lines[i]
        x = [time / 1_000_000_000 for time in times]
        ax.plot(
            x,
            channel_line,
            label="Channel " + str(metadata["channels"][i] + 1),
            linewidth=0.5
        )
    ax.grid(True)
    ax.legend(bbox_to_anchor = (1.05, 1), fancybox=True, shadow=True)
    fig.tight_layout()
    if show_plot:
        plt.show()
    return fig