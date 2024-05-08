def get_providers():
    from ..subtitle_providers.open_subtitles_com import (
        OpenSubtitlesCom,
    )

    # TODO: Sort by priority
    providers = [OpenSubtitlesCom()]
    return [provider for provider in providers if provider.is_enabled()]
