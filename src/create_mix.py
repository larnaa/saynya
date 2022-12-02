import warnings

warnings.filterwarnings('ignore')
from pathlib import Path
from typing import Any

import nussl  # type: ignore
import scaper  # type: ignore

import viz

template_event_parameters = {
    'label': ('const', 'cat'),
    'source_file': ('choose', []),
    'source_time': ('const', 0),
    'event_time': ('const', 0),
    'event_duration': ('const', 5.0),
    'snr': ('uniform', -5, 5),
    'pitch_shift': ('uniform', -2, 2),
    'time_stretch': (None),
}

foreground_folder = Path(__file__).parent.parent / 'foreground'
background_folder = Path(__file__).parent.parent / 'background'


def start_scaper(fg_folder: Path, bg_folder: Path, event_template: dict[str, Any], seed: int) -> scaper:

    soundscape_duration = 5.0

    sc = scaper.Scaper(soundscape_duration, fg_folder, bg_folder, random_state=seed)

    sc.sr = 44100
    sc.ref_db = -30
    sc.n_channels = 1

    labels_background = ['rain', 'vacuum_cleaner', 'wind']

    for label in labels_background:
        sc.add_background(
            label=('const', label),
            source_file=('choose', []),
            source_time=('const', 0),
        )

    sc.add_event(**event_template)

    return sc.generate(fix_clipping=True)


def generate_mixture(
    dataset: nussl.datasets,
    fg_folder: Path,
    bg_folder: Path,
    event_template: dict[str, Any],
    seed: int,
) -> dict[str, Any]:

    # hide warnings
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore')

        data = start_scaper(fg_folder, bg_folder, event_template, seed)

    # unpack the data
    mixture_audio, mixture_jam, annotation_list, stem_audio_list = data

    # convert mixture to nussl format
    mix = dataset._load_audio_from_array(audio_data=mixture_audio, sample_rate=dataset.sample_rate)

    # convert stems to nussl format
    sources = {}
    ann = mixture_jam.annotations.search(namespace='scaper')[0]
    for obs, stem_audio in zip(ann.data, stem_audio_list):
        key = obs.value['label']
        sources[key] = dataset._load_audio_from_array(audio_data=stem_audio, sample_rate=dataset.sample_rate)

    # store the mixture, stems and JAMS annotation in the format expected by nussl
    output = {
        'mix': mix,
        'sources': sources,
        'metadata': mixture_jam,
    }
    return output


def mix_func(dataset: Any, seed: int) -> dict[str, Any]:
    return generate_mixture(
        dataset=dataset,
        fg_folder=foreground_folder,
        bg_folder=background_folder,
        event_template=template_event_parameters,
        seed=seed,
    )


# Create a nussle OnTheFly data generator
on_the_fly = nussl.datasets.OnTheFly(num_mixtures=1000, mix_closure=mix_func)

for i in range(3):
    item: dict[str, Any] = on_the_fly[i]
    mix = item['mix']
    sources = item['sources']

    viz.show_sources(sources)
