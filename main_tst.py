import pandas as pd

from mat.lix_pr import convert_lix_file


def main():
    lid_file = '/home/kaz/Downloads/2503600_TST_20250319_162805.lid'
    rv = convert_lix_file(lid_file)
    csv_file = lid_file.replace('.lid', '.csv')

    # with open(csv_file) as f:
    #     df = pd.read_csv(f)

    # if (not is_rpi) or (is_rpi and r == 'BLE'):
    #     dp = data['Depth (fathoms) TDO']
    #     dt = data['Temperature (F) TDO']
    #     # calculate 80th percentile to ensure bottom sea values
    #     p80 = _percentile(dp, 80)
    #     ls_p, ls_t = [], []
    #     for i, p in enumerate(dp):
    #         if p >= p80:
    #             ls_p.append(dp[i])
    #             ls_t.append(dt[i])
    #     lg.a(f'debug: percentile 80 for TDO data is {p80}')
    #     s = 'haul summary\n'
    #     s += f'{t1}\n{t2}\n'
    #     s += '{:5.2f} fathoms\n'.format(np.nanmean(ls_p))
    #     s += '{:5.2f} °F'.format(np.nanmean(ls_t))
    #     _u(f"{STATE_DDS_BLE_DOWNLOAD_STATISTICS}/{s}")


# test for summary box
if __name__ == '__main__':
    main()
