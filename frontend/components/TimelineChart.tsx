'use client';

import { useEffect, useRef } from 'react';
import * as am5 from '@amcharts/amcharts5';
import * as am5xy from '@amcharts/amcharts5/xy';
import am5themes_Animated from '@amcharts/amcharts5/themes/Animated';
import { api, DateRangeParams } from '@/lib/api-client';

interface TimelineChartProps {
  dateRange?: { from: Date; to: Date } | null;
}

export default function TimelineChart({ dateRange }: TimelineChartProps) {
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
        min: 0,
        max: 100,
        renderer: am5xy.AxisRendererY.new(root, {}),
      })
    );

    // Add series
    const series = chart.series.push(
      am5xy.LineSeries.new(root, {
        name: 'Success Rate',
        xAxis: xAxis,
        yAxis: yAxis,
        valueYField: 'success_rate',
        valueXField: 'timestamp',
        tooltip: am5.Tooltip.new(root, {
          labelText: '{valueY}% - {status}',
        }),
        stroke: am5.color(0x007bff),
        fill: am5.color(0x007bff),
      })
    );

    series.strokes.template.setAll({ strokeWidth: 2 });
    series.fills.template.setAll({ fillOpacity: 0.1, visible: true });

    // Add cursor
    const cursor = chart.set('cursor', am5xy.XYCursor.new(root, {}));
    cursor.lineY.set('visible', false);

    // Load data
    const dateParams: DateRangeParams | undefined = dateRange
      ? { from: dateRange.from, to: dateRange.to }
      : undefined;

    api.getTimeline(dateParams).then((data) => {
      const chartData = data.map((item) => ({
        timestamp: new Date(item.timestamp).getTime(),
        success_rate: item.success_rate,
        status: item.status,
      }));
      series.data.setAll(chartData);
    });

    return () => {
      root.dispose();
    };
  }, [dateRange]);

  return <div ref={chartRef} style={{ width: '100%', height: '300px' }} />;
}
