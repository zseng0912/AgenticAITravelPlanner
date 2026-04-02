import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Slider } from "@/components/ui/slider";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { Calendar } from "@/components/ui/calendar";
import { cn } from "@/lib/utils";
import { format } from "date-fns";
import { CalendarIcon, Sparkles, Check, ChevronsUpDown } from "lucide-react";
import PreferenceChip from "./PreferenceChip";

const PREFERENCES = [
  { label: "Food", icon: "🍜" },
  { label: "Nature", icon: "🌿" },
  { label: "Shopping", icon: "🛍️" },
  { label: "Adventure", icon: "🏔️" },
  { label: "Culture", icon: "🏛️" },
  { label: "Relaxation", icon: "🧘" },
];

interface Airport {
  iata: string;
  name: string;
  city: string;
  country: string;
}

interface AirportSelectProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder: string;
}

/**
 * AirportSelect Component
 * A searchable dropdown for selecting airports/cities.
 * Fetches data from the backend API with debouncing.
 */
const AirportSelect = ({ label, value, onChange, placeholder }: AirportSelectProps) => {
  const [open, setOpen] = useState(false);
  const [airports, setAirports] = useState<Airport[]>([]);
  const [search, setSearch] = useState("");
  const [selectedLabel, setSelectedLabel] = useState("");
  const [loading, setLoading] = useState(false);

  // Fetch airport suggestions when search query changes
  useEffect(() => {
    const fetchAirports = async () => {
      setLoading(true);
      try {
        // Backend endpoint for airport autocomplete
        const response = await fetch(`http://localhost:8000/api/airports/search?q=${search || ""}`);
        const data = await response.json();
        setAirports(data);
      } catch (error) {
        console.error("Error fetching airports:", error);
      } finally {
        setLoading(false);
      }
    };

    // Debounce API calls to avoid excessive requests
    const debounceTimer = setTimeout(fetchAirports, 300);
    return () => clearTimeout(debounceTimer);
  }, [search]);

  return (
    <div className="flex flex-col gap-2">
      <label className="text-sm font-medium text-foreground">{label}</label>
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            role="combobox"
            aria-expanded={open}
            className="w-full justify-between bg-background font-normal"
          >
            {value ? (
              <span className="truncate">
                {selectedLabel || value}
              </span>
            ) : (
              <span className="text-muted-foreground">{placeholder}</span>
            )}
            <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-[var(--radix-popover-trigger-width)] p-0" align="start">
          <Command shouldFilter={false}>
            <CommandInput 
              placeholder="Search airport, city or country..." 
              value={search}
              onValueChange={setSearch}
            />
            <CommandList>
              {loading && <div className="p-4 text-sm text-center text-muted-foreground animate-pulse">Searching airports...</div>}
              {!loading && airports.length === 0 && <CommandEmpty>No airport found.</CommandEmpty>}
              {!loading && airports.length > 0 && (
                <CommandGroup>
                  {airports.map((airport) => (
                    <CommandItem
                      key={airport.iata}
                      value={airport.iata}
                      onSelect={() => {
                        setSelectedLabel(`${airport.city} (${airport.iata})`);
                        onChange(airport.iata);
                        setOpen(false);
                      }}
                      className="flex flex-col items-start py-2 cursor-pointer"
                    >
                      <div className="flex w-full items-center justify-between">
                        <span className="font-semibold">{airport.city} ({airport.iata})</span>
                        <Check
                          className={cn(
                            "ml-2 h-4 w-4",
                            value === airport.iata ? "opacity-100" : "opacity-0"
                          )}
                        />
                      </div>
                      <span className="text-xs text-muted-foreground">
                        {airport.name}, {airport.country}
                      </span>
                    </CommandItem>
                  ))}
                </CommandGroup>
              )}
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>
    </div>
  );
};

interface TravelFormProps {
  onGenerate: (data: any) => void;
  initialData?: any;
}

/**
 * TravelForm Component
 * The main input form for trip planning.
 * Collects departure, destination, dates, budget, and preferences.
 */
const TravelForm = ({ onGenerate, initialData }: TravelFormProps) => {
  // Form State
  const [intent, setIntent] = useState(initialData?.intent || "");
  const [departure, setDeparture] = useState(initialData?.departure || "");
  const [destination, setDestination] = useState(initialData?.destination || "");
  const [startDate, setStartDate] = useState(initialData?.start_date ? new Date(initialData.start_date) : undefined);
  const [endDate, setEndDate] = useState(initialData?.end_date ? new Date(initialData.end_date) : undefined);
  const [budget, setBudget] = useState([initialData?.budget || 3000]);
  const [selectedPrefs, setSelectedPrefs] = useState<string[]>(initialData?.preferences || []);
  const [travelType, setTravelType] = useState(initialData?.travel_type || "");
  const [numPeople, setNumPeople] = useState(initialData?.num_people || 1);

  /**
   * Validates and submits the form data to the parent component.
   */
  const handleGenerate = () => {
    if (!departure || !destination || !startDate || !endDate || !travelType) {
      alert("Please fill in all required fields");
      return;
    }

    onGenerate({
      intent: intent || `Trip from ${departure} to ${destination}`,
      departure,
      destination,
      start_date: format(startDate, "yyyy-MM-dd"),
      end_date: format(endDate, "yyyy-MM-dd"),
      budget: budget[0],
      preferences: selectedPrefs,
      travel_type: travelType,
      num_people: numPeople,
    });
  };

  const togglePref = (label: string) => {
    setSelectedPrefs((prev) =>
      prev.includes(label) ? prev.filter((p) => p !== label) : [...prev, label]
    );
  };

  return (
    <div className="bg-card rounded-2xl shadow-sm border border-border p-6 md:p-8 animate-fade-in">
      <h2 className="text-xl font-semibold mb-6 text-card-foreground">
        ✈️ Tell us about your dream trip
      </h2>

      <div className="space-y-6">
        {/* Departure */}
        <AirportSelect
          label="Departure"
          placeholder="Select departure airport"
          value={departure}
          onChange={setDeparture}
        />

        {/* Destination */}
        <AirportSelect
          label="Destination"
          placeholder="Select destination airport"
          value={destination}
          onChange={setDestination}
        />

        {/* Dates */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Start Date
            </label>
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className={cn(
                    "w-full justify-start text-left font-normal",
                    !startDate && "text-muted-foreground"
                  )}
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {startDate ? format(startDate, "PPP") : "Pick a date"}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="start">
                <Calendar
                  mode="single"
                  selected={startDate}
                  onSelect={setStartDate}
                  initialFocus
                  className="p-3 pointer-events-auto"
                />
              </PopoverContent>
            </Popover>
          </div>
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              End Date
            </label>
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className={cn(
                    "w-full justify-start text-left font-normal",
                    !endDate && "text-muted-foreground"
                  )}
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {endDate ? format(endDate, "PPP") : "Pick a date"}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="start">
                <Calendar
                  mode="single"
                  selected={endDate}
                  onSelect={setEndDate}
                  initialFocus
                  className="p-3 pointer-events-auto"
                />
              </PopoverContent>
            </Popover>
          </div>
        </div>

        {/* Budget */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            Budget: <span className="text-primary font-semibold">RM {budget[0].toLocaleString()}</span>
          </label>
          <Slider
            value={budget}
            onValueChange={setBudget}
            min={500}
            max={20000}
            step={100}
            className="mt-2"
          />
          <div className="flex justify-between text-xs text-muted-foreground mt-1">
            <span>RM 500</span>
            <span>RM 20,000</span>
          </div>
        </div>

        {/* Preferences */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-3">
            Travel Preferences
          </label>
          <div className="flex flex-wrap gap-2">
            {PREFERENCES.map((p) => (
              <PreferenceChip
                key={p.label}
                label={p.label}
                icon={p.icon}
                selected={selectedPrefs.includes(p.label)}
                onClick={() => togglePref(p.label)}
              />
            ))}
          </div>
        </div>

        {/* Travel Type */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Travel Type
            </label>
            <Select value={travelType} onValueChange={(val) => {
              setTravelType(val);
              if (val === "solo") setNumPeople(1);
              if (val === "couple") setNumPeople(2);
            }}>
              <SelectTrigger className="bg-background">
                <SelectValue placeholder="Select travel type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="solo">Solo</SelectItem>
                <SelectItem value="couple">Couple</SelectItem>
                <SelectItem value="family">Family</SelectItem>
                <SelectItem value="friends">Friends</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {(travelType === "family" || travelType === "friends") && (
            <div className="animate-in fade-in slide-in-from-top-2 duration-300">
              <label className="block text-sm font-medium text-foreground mb-2">
                Number of People
              </label>
              <Input
                type="number"
                min={1}
                max={20}
                value={numPeople}
                onChange={(e) => setNumPeople(parseInt(e.target.value) || 1)}
                className="bg-background"
              />
            </div>
          )}
        </div>

        {/* Intent */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            What kind of trip are you looking for? (Additional Details)
          </label>
          <Textarea
            placeholder="e.g. Plan a 5-day trip to Japan under RM5000, love food and nature"
            value={intent}
            onChange={(e) => setIntent(e.target.value)}
            className="min-h-[100px] resize-none bg-background text-foreground placeholder:text-muted-foreground"
          />
        </div>

        {/* Generate */}
        <Button
          size="lg"
          className="w-full text-base font-semibold h-12 rounded-xl"
          onClick={handleGenerate}
        >
          <Sparkles className="mr-2 h-5 w-5" />
          Generate Travel Plan
        </Button>
      </div>
    </div>
  );
};

export default TravelForm;
