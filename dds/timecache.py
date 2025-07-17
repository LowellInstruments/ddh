from cacheout import Cache
import time


TIM_CACHE_MAX_SIZE = 1024
_g_timecache = Cache(
    maxsize=TIM_CACHE_MAX_SIZE,
    ttl=0,
    timer=time.time,
    default=None
)



def time_cache_get_keys_length():
    n = len(_g_timecache.keys())
    print(f'used keys {n} / {TIM_CACHE_MAX_SIZE}')


def annotate_time_this_occurred(k, t, pre_rm=False):
    if t <= 0:
        return
    if pre_rm and _g_timecache.has(k):
        _g_timecache.delete(k)
    _g_timecache.add(k, k, ttl=t)


def delete_annotation(k):
    if _g_timecache.has(k):
        _g_timecache.delete(k)


def delete_all_annotations_by_mask(mask):
    for k in _g_timecache.keys():
        if k.startswith(mask):
            _g_timecache.delete(k)


def show_all_annotations_by_mask(mask):
    print(f'showing all annotations mask {mask}')
    for k in _g_timecache.keys():
        if k.startswith(mask):
            print(_g_timecache.get(k))
            print(_g_timecache.get_ttl(k))


def delete_all_annotations():
    for k in _g_timecache.keys():
        _g_timecache.delete(k)


def is_it_time_to(k, t, annotate=True):
    if not _g_timecache.has(k):
        if annotate:
            annotate_time_this_occurred(k, t)
        return True

    # not enough time passed since last occurrence of this
    return False


def query_is_it_time_to(k):
    return not _g_timecache.has(k)


# test
if __name__ == '__main__':
    annotate_time_this_occurred('k', 10)
    delete_all_annotations_by_mask('k')
    rv = is_it_time_to('k', 0, annotate=False)
    print(rv)

