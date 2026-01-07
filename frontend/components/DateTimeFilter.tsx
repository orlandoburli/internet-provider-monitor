'use client';

import { useState } from 'react';
import { Calendar as CalendarIcon, Clock } from 'lucide-react';
import { format, startOfDay, endOfDay, subDays, subHours } from 'date-fns';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';

export type DateRange = {
  from: Date;
  to: Date;
};

export type PeriodType = 'custom' | 'last-hour' | 'last-6-hours' | 'last-24-hours' | 'today' | 'yesterday' | 'last-7-days' | 'last-30-days';

interface DateTimeFilterProps {
  onFilterChange: (range: DateRange, type: PeriodType) => void;
}

export default function DateTimeFilter({ onFilterChange }: DateTimeFilterProps) {
  const [periodType, setPeriodType] = useState<PeriodType>('last-24-hours');
  const [customDate, setCustomDate] = useState<Date>(new Date());
  const [customFromDate, setCustomFromDate] = useState<Date>(subDays(new Date(), 1));
  const [customToDate, setCustomToDate] = useState<Date>(new Date());
  const [startHour, setStartHour] = useState<string>('00');
  const [endHour, setEndHour] = useState<string>('23');

  const getPeriodRange = (type: PeriodType): DateRange => {
    const now = new Date();
    
    switch (type) {
      case 'last-hour':
        return { from: subHours(now, 1), to: now };
      case 'last-6-hours':
        return { from: subHours(now, 6), to: now };
      case 'last-24-hours':
        return { from: subHours(now, 24), to: now };
      case 'today':
        return { from: startOfDay(now), to: endOfDay(now) };
      case 'yesterday': {
        const yesterday = subDays(now, 1);
        return { from: startOfDay(yesterday), to: endOfDay(yesterday) };
      }
      case 'last-7-days':
        return { from: subDays(now, 7), to: now };
      case 'last-30-days':
        return { from: subDays(now, 30), to: now };
      case 'custom': {
        const from = new Date(customFromDate);
        from.setHours(parseInt(startHour), 0, 0, 0);
        const to = new Date(customToDate);
        to.setHours(parseInt(endHour), 59, 59, 999);
        return { from, to };
      }
      default:
        return { from: subHours(now, 24), to: now };
    }
  };

  const handlePeriodChange = (newType: PeriodType) => {
    setPeriodType(newType);
    const range = getPeriodRange(newType);
    onFilterChange(range, newType);
  };

  const handleCustomDateChange = () => {
    const range = getPeriodRange('custom');
    onFilterChange(range, 'custom');
  };

  const hours = Array.from({ length: 24 }, (_, i) => i.toString().padStart(2, '0'));

  return (
    <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium flex items-center gap-2">
          <CalendarIcon className="h-4 w-4" />
          Period Filter
        </h3>
        {periodType !== 'custom' && (
          <Badge variant="secondary" className="text-xs">
            {periodType.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
          </Badge>
        )}
      </div>

      {/* Quick Period Selection */}
      <div className="space-y-2">
        <label className="text-xs text-muted-foreground">Quick Select</label>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          <Button
            variant={periodType === 'last-hour' ? 'default' : 'outline'}
            size="sm"
            onClick={() => handlePeriodChange('last-hour')}
            className="text-xs"
          >
            Last Hour
          </Button>
          <Button
            variant={periodType === 'last-6-hours' ? 'default' : 'outline'}
            size="sm"
            onClick={() => handlePeriodChange('last-6-hours')}
            className="text-xs"
          >
            Last 6 Hours
          </Button>
          <Button
            variant={periodType === 'last-24-hours' ? 'default' : 'outline'}
            size="sm"
            onClick={() => handlePeriodChange('last-24-hours')}
            className="text-xs"
          >
            Last 24 Hours
          </Button>
          <Button
            variant={periodType === 'today' ? 'default' : 'outline'}
            size="sm"
            onClick={() => handlePeriodChange('today')}
            className="text-xs"
          >
            Today
          </Button>
          <Button
            variant={periodType === 'yesterday' ? 'default' : 'outline'}
            size="sm"
            onClick={() => handlePeriodChange('yesterday')}
            className="text-xs"
          >
            Yesterday
          </Button>
          <Button
            variant={periodType === 'last-7-days' ? 'default' : 'outline'}
            size="sm"
            onClick={() => handlePeriodChange('last-7-days')}
            className="text-xs"
          >
            Last 7 Days
          </Button>
          <Button
            variant={periodType === 'last-30-days' ? 'default' : 'outline'}
            size="sm"
            onClick={() => handlePeriodChange('last-30-days')}
            className="text-xs"
          >
            Last 30 Days
          </Button>
          <Button
            variant={periodType === 'custom' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setPeriodType('custom')}
            className="text-xs"
          >
            Custom
          </Button>
        </div>
      </div>

      {/* Custom Date Range */}
      {periodType === 'custom' && (
        <div className="space-y-3 p-3 bg-zinc-50 dark:bg-zinc-800 rounded-md">
          <label className="text-xs font-medium text-muted-foreground">Custom Date & Time Range</label>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* From Date & Hour */}
            <div className="space-y-2">
              <label className="text-xs text-muted-foreground">From</label>
              <div className="flex gap-2">
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className="flex-1 justify-start text-left font-normal text-xs"
                    >
                      <CalendarIcon className="mr-2 h-3 w-3" />
                      {format(customFromDate, 'MMM dd, yyyy')}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0" align="start">
                    <Calendar
                      mode="single"
                      selected={customFromDate}
                      onSelect={(date) => date && setCustomFromDate(date)}
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
                
                <Select value={startHour} onValueChange={setStartHour}>
                  <SelectTrigger className="w-20">
                    <Clock className="h-3 w-3 mr-1" />
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {hours.map((hour) => (
                      <SelectItem key={hour} value={hour}>
                        {hour}:00
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* To Date & Hour */}
            <div className="space-y-2">
              <label className="text-xs text-muted-foreground">To</label>
              <div className="flex gap-2">
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className="flex-1 justify-start text-left font-normal text-xs"
                    >
                      <CalendarIcon className="mr-2 h-3 w-3" />
                      {format(customToDate, 'MMM dd, yyyy')}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0" align="start">
                    <Calendar
                      mode="single"
                      selected={customToDate}
                      onSelect={(date) => date && setCustomToDate(date)}
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
                
                <Select value={endHour} onValueChange={setEndHour}>
                  <SelectTrigger className="w-20">
                    <Clock className="h-3 w-3 mr-1" />
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {hours.map((hour) => (
                      <SelectItem key={hour} value={hour}>
                        {hour}:59
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          <Button 
            onClick={handleCustomDateChange} 
            className="w-full"
            size="sm"
          >
            Apply Custom Filter
          </Button>
        </div>
      )}

      {/* Current Range Display */}
      <div className="pt-2 border-t border-zinc-200 dark:border-zinc-800">
        <p className="text-xs text-muted-foreground">
          <strong>Current Range:</strong>{' '}
          {format(getPeriodRange(periodType).from, 'MMM dd, yyyy HH:mm')} -{' '}
          {format(getPeriodRange(periodType).to, 'MMM dd, yyyy HH:mm')}
        </p>
      </div>
    </div>
  );
}
