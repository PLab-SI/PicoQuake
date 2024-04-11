/*
This header provides a set of ICMP42688P anti-alias filter (second order low-pass) configurations.
For register value source see tabel in section 5.3 of the datasheet.
datasheet: https://invensense.tdk.com/wp-content/uploads/2020/04/ds-000347_icm-42688-p-datasheet.pdf

*/

#ifndef ICM42688P_FILTER_CONFIG_H
#define ICM42688P_FILTER_CONFIG_H

#include <stdint.h>

struct FilterConfig {
  const uint16_t bandwidth_hz;
  const uint16_t aaf_delt;
  const uint16_t aaf_deltsqr;
  const uint16_t aaf_bitshift;
};



namespace filter_config {
  static constexpr FilterConfig f_42hz = {
    .bandwidth_hz = 42,
    .aaf_delt = 1,
    .aaf_deltsqr = 1,
    .aaf_bitshift = 15
  };

  static constexpr FilterConfig f_84hz = {
      .bandwidth_hz = 84,
      .aaf_delt = 2,
      .aaf_deltsqr = 4,
      .aaf_bitshift = 13
  };

  static constexpr FilterConfig f_126hz = {
      .bandwidth_hz = 126,
      .aaf_delt = 3,
      .aaf_deltsqr = 9,
      .aaf_bitshift = 12
  };

  static constexpr FilterConfig f_170hz = {
      .bandwidth_hz = 170,
      .aaf_delt = 4,
      .aaf_deltsqr = 16,
      .aaf_bitshift = 11
  };

  static constexpr FilterConfig f_213hz = {
      .bandwidth_hz = 213,
      .aaf_delt = 5,
      .aaf_deltsqr = 25,
      .aaf_bitshift = 10
  };

  static constexpr FilterConfig f_258hz = {
      .bandwidth_hz = 258,
      .aaf_delt = 6,
      .aaf_deltsqr = 36,
      .aaf_bitshift = 10
  };

  static constexpr FilterConfig f_303hz = {
      .bandwidth_hz = 303,
      .aaf_delt = 7,
      .aaf_deltsqr = 49,
      .aaf_bitshift = 9
  };

  static constexpr FilterConfig f_348hz = {
      .bandwidth_hz = 348,
      .aaf_delt = 8,
      .aaf_deltsqr = 64,
      .aaf_bitshift = 9
  };

  static constexpr FilterConfig f_394hz = {
      .bandwidth_hz = 394,
      .aaf_delt = 9,
      .aaf_deltsqr = 81,
      .aaf_bitshift = 9
  };

  static constexpr FilterConfig f_441hz = {
      .bandwidth_hz = 441,
      .aaf_delt = 10,
      .aaf_deltsqr = 100,
      .aaf_bitshift = 8
  };

  static constexpr FilterConfig f_488hz = {
      .bandwidth_hz = 488,
      .aaf_delt = 11,
      .aaf_deltsqr = 122,
      .aaf_bitshift = 8
  };

  static constexpr FilterConfig f_536hz = {
      .bandwidth_hz = 536,
      .aaf_delt = 12,
      .aaf_deltsqr = 144,
      .aaf_bitshift = 8
  };

  static constexpr FilterConfig f_585hz = {
      .bandwidth_hz = 585,
      .aaf_delt = 13,
      .aaf_deltsqr = 170,
      .aaf_bitshift = 8
  };

  static constexpr FilterConfig f_634hz = {
      .bandwidth_hz = 634,
      .aaf_delt = 14,
      .aaf_deltsqr = 196,
      .aaf_bitshift = 7
  };

  static constexpr FilterConfig f_684hz = {
      .bandwidth_hz = 684,
      .aaf_delt = 15,
      .aaf_deltsqr = 224,
      .aaf_bitshift = 7
  };

  static constexpr FilterConfig f_734hz = {
      .bandwidth_hz = 734,
      .aaf_delt = 16,
      .aaf_deltsqr = 256,
      .aaf_bitshift = 7
  };

  static constexpr FilterConfig f_785hz = {
      .bandwidth_hz = 785,
      .aaf_delt = 17,
      .aaf_deltsqr = 288,
      .aaf_bitshift = 7
  };

  static constexpr FilterConfig f_837hz = {
      .bandwidth_hz = 837,
      .aaf_delt = 18,
      .aaf_deltsqr = 324,
      .aaf_bitshift = 7
  };

  static constexpr FilterConfig f_890hz = {
      .bandwidth_hz = 890,
      .aaf_delt = 19,
      .aaf_deltsqr = 360,
      .aaf_bitshift = 6
  };

  static constexpr FilterConfig f_943hz = {
      .bandwidth_hz = 943,
      .aaf_delt = 20,
      .aaf_deltsqr = 400,
      .aaf_bitshift = 6
  };

  static constexpr FilterConfig f_997hz = {
      .bandwidth_hz = 997,
      .aaf_delt = 21,
      .aaf_deltsqr = 440,
      .aaf_bitshift = 6
  };

  static constexpr FilterConfig f_1051hz = {
      .bandwidth_hz = 1051,
      .aaf_delt = 22,
      .aaf_deltsqr = 488,
      .aaf_bitshift = 6
  };

  static constexpr FilterConfig f_1107hz = {
      .bandwidth_hz = 1107,
      .aaf_delt = 23,
      .aaf_deltsqr = 528,
      .aaf_bitshift = 6
  };

  static constexpr FilterConfig f_1163hz = {
      .bandwidth_hz = 1163,
      .aaf_delt = 24,
      .aaf_deltsqr = 576,
      .aaf_bitshift = 6
  };

  static constexpr FilterConfig f_1220hz = {
      .bandwidth_hz = 1220,
      .aaf_delt = 25,
      .aaf_deltsqr = 624,
      .aaf_bitshift = 6
  };

  static constexpr FilterConfig f_1277hz = {
      .bandwidth_hz = 1277,
      .aaf_delt = 26,
      .aaf_deltsqr = 680,
      .aaf_bitshift = 6
  };

  static constexpr FilterConfig f_1336hz = {
      .bandwidth_hz = 1336,
      .aaf_delt = 27,
      .aaf_deltsqr = 736,
      .aaf_bitshift = 5
  };

  static constexpr FilterConfig f_1395hz = {
      .bandwidth_hz = 1395,
      .aaf_delt = 28,
      .aaf_deltsqr = 784,
      .aaf_bitshift = 5
  };

  static constexpr FilterConfig f_1454hz = {
      .bandwidth_hz = 1454,
      .aaf_delt = 29,
      .aaf_deltsqr = 848,
      .aaf_bitshift = 5
  };

  static constexpr FilterConfig f_1515hz = {
      .bandwidth_hz = 1515,
      .aaf_delt = 30,
      .aaf_deltsqr = 896,
      .aaf_bitshift = 5
  };

  static constexpr FilterConfig f_1577hz = {
      .bandwidth_hz = 1577,
      .aaf_delt = 31,
      .aaf_deltsqr = 960,
      .aaf_bitshift = 5
  };

  static constexpr FilterConfig f_1639hz = {
      .bandwidth_hz = 1639,
      .aaf_delt = 32,
      .aaf_deltsqr = 1024,
      .aaf_bitshift = 5
  };

  static constexpr FilterConfig f_1702hz = {
      .bandwidth_hz = 1702,
      .aaf_delt = 33,
      .aaf_deltsqr = 1088,
      .aaf_bitshift = 5
  };

  static constexpr FilterConfig f_1766hz = {
      .bandwidth_hz = 1766,
      .aaf_delt = 34,
      .aaf_deltsqr = 1152,
      .aaf_bitshift = 5
  };

  static constexpr FilterConfig f_1830hz = {
      .bandwidth_hz = 1830,
      .aaf_delt = 35,
      .aaf_deltsqr = 1232,
      .aaf_bitshift = 5
  };

  static constexpr FilterConfig f_1896hz = {
      .bandwidth_hz = 1896,
      .aaf_delt = 36,
      .aaf_deltsqr = 1296,
      .aaf_bitshift = 5
  };

  static constexpr FilterConfig f_1962hz = {
      .bandwidth_hz = 1962,
      .aaf_delt = 37,
      .aaf_deltsqr = 1376,
      .aaf_bitshift = 4
  };

  static constexpr FilterConfig f_2029hz = {
      .bandwidth_hz = 2029,
      .aaf_delt = 38,
      .aaf_deltsqr = 1440,
      .aaf_bitshift = 4
  };

  static constexpr FilterConfig f_2097hz = {
      .bandwidth_hz = 2097,
      .aaf_delt = 39,
      .aaf_deltsqr = 1536,
      .aaf_bitshift = 4
  };

  static constexpr FilterConfig f_2166hz = {
      .bandwidth_hz = 2166,
      .aaf_delt = 40,
      .aaf_deltsqr = 1600,
      .aaf_bitshift = 4
  };

  static constexpr FilterConfig f_2235hz = {
      .bandwidth_hz = 2235,
      .aaf_delt = 41,
      .aaf_deltsqr = 1696,
      .aaf_bitshift = 4
  };

  static constexpr FilterConfig f_2306hz = {
      .bandwidth_hz = 2306,
      .aaf_delt = 42,
      .aaf_deltsqr = 1760,
      .aaf_bitshift = 4
  };

  static constexpr FilterConfig f_2377hz = {
      .bandwidth_hz = 2377,
      .aaf_delt = 43,
      .aaf_deltsqr = 1856,
      .aaf_bitshift = 4
  };

  static constexpr FilterConfig f_2449hz = {
      .bandwidth_hz = 2449,
      .aaf_delt = 44,
      .aaf_deltsqr = 1952,
      .aaf_bitshift = 4
  };

  static constexpr FilterConfig f_2522hz = {
      .bandwidth_hz = 2522,
      .aaf_delt = 45,
      .aaf_deltsqr = 2016,
      .aaf_bitshift = 4
  };

  static constexpr FilterConfig f_2596hz = {
      .bandwidth_hz = 2596,
      .aaf_delt = 46,
      .aaf_deltsqr = 2112,
      .aaf_bitshift = 4
  };

  static constexpr FilterConfig f_2671hz = {
      .bandwidth_hz = 2671,
      .aaf_delt = 47,
      .aaf_deltsqr = 2208,
      .aaf_bitshift = 4
  };

  static constexpr FilterConfig f_2746hz = {
      .bandwidth_hz = 2746,
      .aaf_delt = 48,
      .aaf_deltsqr = 2304,
      .aaf_bitshift = 4
  };

  static constexpr FilterConfig f_2823hz = {
      .bandwidth_hz = 2823,
      .aaf_delt = 49,
      .aaf_deltsqr = 2400,
      .aaf_bitshift = 4
  };

  static constexpr FilterConfig f_2900hz = {
      .bandwidth_hz = 2900,
      .aaf_delt = 50,
      .aaf_deltsqr = 2496,
      .aaf_bitshift = 4
  };

  static constexpr FilterConfig f_2978hz = {
      .bandwidth_hz = 2978,
      .aaf_delt = 51,
      .aaf_deltsqr = 2592,
      .aaf_bitshift = 4
  };

  static constexpr FilterConfig f_3057hz = {
      .bandwidth_hz = 3057,
      .aaf_delt = 52,
      .aaf_deltsqr = 2720,
      .aaf_bitshift = 4
  };

  static constexpr FilterConfig f_3137hz = {
      .bandwidth_hz = 3137,
      .aaf_delt = 53,
      .aaf_deltsqr = 2816,
      .aaf_bitshift = 3
  };

  static constexpr FilterConfig f_3217hz = {
      .bandwidth_hz = 3217,
      .aaf_delt = 54,
      .aaf_deltsqr = 2944,
      .aaf_bitshift = 3
  };

  static constexpr FilterConfig f_3299hz = {
      .bandwidth_hz = 3299,
      .aaf_delt = 55,
      .aaf_deltsqr = 3008,
      .aaf_bitshift = 3
  };

  static constexpr FilterConfig f_3381hz = {
      .bandwidth_hz = 3381,
      .aaf_delt = 56,
      .aaf_deltsqr = 3136,
      .aaf_bitshift = 3
  };

  static constexpr FilterConfig f_3464hz = {
      .bandwidth_hz = 3464,
      .aaf_delt = 57,
      .aaf_deltsqr = 3264,
      .aaf_bitshift = 3
  };

  static constexpr FilterConfig f_3548hz = {
      .bandwidth_hz = 3548,
      .aaf_delt = 58,
      .aaf_deltsqr = 3392,
      .aaf_bitshift = 3
  };

  static constexpr FilterConfig f_3633hz = {
      .bandwidth_hz = 3633,
      .aaf_delt = 59,
      .aaf_deltsqr = 3456,
      .aaf_bitshift = 3
  };

  static constexpr FilterConfig f_3718hz = {
      .bandwidth_hz = 3718,
      .aaf_delt = 60,
      .aaf_deltsqr = 3584,
      .aaf_bitshift = 3
  };

  static constexpr FilterConfig f_3805hz = {
      .bandwidth_hz = 3805,
      .aaf_delt = 61,
      .aaf_deltsqr = 3712,
      .aaf_bitshift = 3
  };

  static constexpr FilterConfig f_3892hz = {
      .bandwidth_hz = 3892,
      .aaf_delt = 62,
      .aaf_deltsqr = 3840,
      .aaf_bitshift = 3
  };

  static constexpr FilterConfig f_3979hz = {
      .bandwidth_hz = 3979,
      .aaf_delt = 63,
      .aaf_deltsqr = 3968,
      .aaf_bitshift = 3
  };

}

// static constexpr const FilterConfig* filter_configss[] = {
//   &filter_config::f_42hz,
//   &filter_config::f_84hz,
//   // ... rest of the elements ...
//   &filter_config::f_3979hz
// };

// all of filter configs in array
static constexpr FilterConfig filter_configs[] = {
  filter_config::f_42hz,
  filter_config::f_84hz,
  filter_config::f_126hz,
  filter_config::f_170hz,
  filter_config::f_213hz,
  filter_config::f_258hz,
  filter_config::f_303hz,
  filter_config::f_348hz,
  filter_config::f_394hz,
  filter_config::f_441hz,
  filter_config::f_488hz,
  filter_config::f_536hz,
  filter_config::f_585hz,
  filter_config::f_634hz,
  filter_config::f_684hz,
  filter_config::f_734hz,
  filter_config::f_785hz,
  filter_config::f_837hz,
  filter_config::f_890hz,
  filter_config::f_943hz,
  filter_config::f_997hz,
  filter_config::f_1051hz,
  filter_config::f_1107hz,
  filter_config::f_1163hz,
  filter_config::f_1220hz,
  filter_config::f_1277hz,
  filter_config::f_1336hz,
  filter_config::f_1395hz,
  filter_config::f_1454hz,
  filter_config::f_1515hz,
  filter_config::f_1577hz,
  filter_config::f_1639hz,
  filter_config::f_1702hz,
  filter_config::f_1766hz,
  filter_config::f_1830hz,
  filter_config::f_1896hz,
  filter_config::f_1962hz,
  filter_config::f_2029hz,
  filter_config::f_2097hz,
  filter_config::f_2166hz,
  filter_config::f_2235hz,
  filter_config::f_2306hz,
  filter_config::f_2377hz,
  filter_config::f_2449hz,
  filter_config::f_2522hz,
  filter_config::f_2596hz,
  filter_config::f_2671hz,
  filter_config::f_2746hz,
  filter_config::f_2823hz,
  filter_config::f_2900hz,
  filter_config::f_2978hz,
  filter_config::f_3057hz,
  filter_config::f_3137hz,
  filter_config::f_3217hz,
  filter_config::f_3299hz,
  filter_config::f_3381hz,
  filter_config::f_3464hz,
  filter_config::f_3548hz,
  filter_config::f_3633hz,
  filter_config::f_3718hz,
  filter_config::f_3805hz,
  filter_config::f_3892hz,
  filter_config::f_3979hz
};


#endif // ICM42688P_FILTER_CONFIG_H