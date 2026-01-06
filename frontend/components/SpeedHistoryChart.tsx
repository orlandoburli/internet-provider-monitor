'use client';

import { useEffect, useRef } from 'react';
import * as am5 from '@amcharts/amcharts5';
import * as am5xy from '@amcharts/amcharts5/xy';
import am5themes_Animated from '@amcharts/amcharts5/themes/Animated';
import { api } from '@/lib/api-client';

export default function SpeedHistoryChart() {
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    // Create root
    const root = am5.Root.new(chartRef.current);
    root.setThemes([am5themes_Animated.new(root)]);

    // Create chart
    const chart = root.container.children.push(
      am5xy.XYChart.new(root, {
        panX: true,
        panY: false,
        wheelX: 'panX',
        wheelY: 'zoomX',
        pinchZoomX: true,
      })
    );

    // Create axes
    const xAxis = chart.xAxes.push(
      am5xy.DateAxis.new(root, {
        maxDeviation: 0.2,
        baseInterval: { timeUnit: 'minute', count: 1 },
        renderer: am5xy.AxisRendererX.new(root, {}),
        tooltip: am5.Tooltip.new(root, {}),
      })
    );

    const yAxis = chart.yAxes.push(
      am5xy.ValueAxis.new(root, {
        renderer: am5xy.AxisRendererY.new(root, {}),
      })
    );

    // Add legend
    const legend = chart.children.push(
      am5.Legend.new(root, {
        centerX: am5.percent(50),
        x: am5.percent(50),
      })
    );

    // Provider colors
    const providerColors: { [key: string]: number } = {
      'speedtest.net': 0xff6384,
      'speed.cloudflare.com': 0x36a2eb,
      'proof.ovh.net': 0x4bc0c0,
    };

    // Load data and create series
    api.getSpeedHistory(24).then((data) => {
      const providerData: { [key: string]: any[] } = {};

      // Group data by provider
      data.forEach((item) => {
        if (!providerData[item.provider]) {
          providerData[item.provider] = [];
        }
        providerData[item.provider].push({
          timestamp: new Date(item.timestamp).getTime(),
          download: item.download_mbps,
          upload: item.upload_mbps,
        });
      });

      // Create series for each provider
      Object.keys(providerData).forEach((provider) => {
        // Download series (solid line)
        const downloadSeries = chart.series.push(
          am5xy.LineSeries.new(root, {
            name: `${provider} - Download`,
            xAxis: xAxis,
            yAxis: yAxis,
            valueYField: 'download',
            valueXField: 'timestamp',
            tooltip: am5.Tooltip.new(root, {
              labelText: '{name}: {valueY} Mbps',
            }),
            stroke: am5.color(providerColors[provider] || 0x999999),
          })
        );

        downloadSeries.strokes.template.setAll({ strokeWidth: 2 });
        downloadSeries.data.setAll(providerData[provider]);

        // Upload series (dashed line)
        if (providerData[provider].some((d: any) => d.upload !== null)) {
          const uploadSeries = chart.series.push(
            am5xy.LineSeries.new(root, {
              name: `${provider} - Upload`,
              xAxis: xAxis,
              yAxis: yAxis,
              valueYField: 'upload',
              valueXField: 'timestamp',
              tooltip: am5.Tooltip.new(root, {
                labelText: '{name}: {valueY} Mbps',
              }),
              stroke: am5.color(providerColors[provider] || 0x999999),
            })
          );

          uploadSeries.strokes.template.setAll({
            strokeWidth: 2,
            strokeDasharray: [5, 5],
          });
          uploadSeries.data.setAll(providerData[provider]);
        }
      });

      legend.data.setAll(chart.series.values);
    });

    // Add cursor
    const cursor = chart.set('cursor', am5xy.XYCursor.new(root, {}));
    cursor.lineY.set('visible', false);

    return () => {
      root.dispose();
    };
  }, []);

  return <div ref={chartRef} style={{ width: '100%', height: '400px' }} />;
}
