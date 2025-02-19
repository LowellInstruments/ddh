from ddh.preferences import preferences_get_models_index, preferences_set_models_index, \
    preferences_get_brightness_clicks

if __name__ == '__main__':
    mi = preferences_get_models_index()
    print('mi', mi)
    preferences_set_models_index(3)
    mi = preferences_get_models_index()
    print('mi', mi)

    b = preferences_get_brightness_clicks()
    print('b', b)
