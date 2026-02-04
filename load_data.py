from matplotlib import pyplot as plt
from gui_components.channel_name_utils import get_channel_name


def plot_intensity_data(channels_lines, times, metadata, show_plot=True):
    fig, ax = plt.subplots()
    ax.set_xlabel(f"Time (s)")
    ax.set_ylabel("Intensity (counts)")
    ax.set_title(
      "Intensity Tracing"
    )
    # plot all channels data
    # Get channel_names from metadata for labels
    channel_names_from_file = metadata.get("channel_names", {})
    for i in range(len(metadata["channels"])):
        channel_line = channels_lines[i]
        channel_id = metadata["channels"][i]
        channel_label = get_channel_name(channel_id, channel_names_from_file)
        x = [time / 1_000_000_000 for time in times]
        ax.plot(
            x,
            channel_line,
            label=channel_label,
            linewidth=0.5
        )
    ax.grid(True)
    ax.legend(bbox_to_anchor = (1.05, 1), fancybox=True, shadow=True)
    fig.tight_layout()
    if show_plot:
        plt.show()
    return fig