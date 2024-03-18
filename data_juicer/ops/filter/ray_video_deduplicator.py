import hashlib

from data_juicer.utils.mm_utils import load_data_with_context, load_video

from ..base_op import OPERATORS
from ..op_fusion import LOADED_VIDEOS
from .ray_basic_deduplicator import RayBasicDeduplicator

OP_NAME = 'ray_video_deduplicator'


@OPERATORS.register_module(OP_NAME)
@LOADED_VIDEOS.register_module(OP_NAME)
class RayVideoDeduplicator(RayBasicDeduplicator):
    """
    Deduplicator to deduplicate samples at document-level using exact matching
    of videos between documents.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialization.

        :param args: extra args
        :param kwargs: extra args
        """
        super().__init__(*args, **kwargs)

    def calculate_hash(self, sample, context=False):
        if self.video_key not in sample or not sample[self.video_key]:
            return RayBasicDeduplicator.EMPTY_HASH_VALUE

        # load videos
        loaded_video_keys = sample[self.video_key]
        sample, videos = load_data_with_context(sample, context,
                                                loaded_video_keys, load_video)
        # compute hash
        md5_hash = hashlib.md5()
        for key in videos:
            # consider the multi stream of video in one container
            for packet in videos[key].demux():
                if packet.stream.type == 'video':
                    md5_hash.update(bytes(packet))

        return md5_hash.hexdigest()
