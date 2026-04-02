import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Clock, MapPin, RefreshCw, Settings2, ChevronDown, ExternalLink, Ticket, DollarSign, Plane, ArrowRight, Hotel, Star } from "lucide-react";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface Activity {
  time: string;
  location: string;
  desc: string;
  image: string;
  price?: string;
  details: string;
  mapsLink: string;
  bookingUrl?: string;
  bookingLabel?: string;
}

const MOCK_ITINERARY = [
  {
    day: 1,
    title: "Arrival & Shibuya",
    activities: [
      { time: "10:00 AM", location: "Narita Airport → Hotel Check-in", desc: "Arrive and settle in at Shinjuku", image: "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=600&q=80", price: "Free", details: "Take the Narita Express (N'EX) to Shinjuku Station. Your hotel is a 5-min walk from the station. Check-in is from 3 PM but luggage can be stored earlier.", mapsLink: "https://maps.google.com/?q=Shinjuku+Station+Tokyo", bookingUrl: "https://example.com/hotel", bookingLabel: "Book Hotel" },
      { time: "1:00 PM", location: "Tsukiji Outer Market", desc: "Fresh sushi lunch & street food tour", image: "https://images.unsplash.com/photo-1553621042-f6e147245754?w=600&q=80", price: "RM 80–150", details: "Explore the bustling outer market stalls. Must-try: tamagoyaki, fresh uni, and tuna sushi. The market is most lively before 2 PM.", mapsLink: "https://maps.google.com/?q=Tsukiji+Outer+Market" },
      { time: "4:00 PM", location: "Shibuya Crossing", desc: "Explore Shibuya & Hachiko statue", image: "https://images.unsplash.com/photo-1542051841857-5f90071e7989?w=600&q=80", price: "Free", details: "Visit the world's busiest pedestrian crossing. See the Hachiko memorial statue and explore the surrounding shops including Shibuya 109.", mapsLink: "https://maps.google.com/?q=Shibuya+Crossing+Tokyo" },
      { time: "7:00 PM", location: "Omoide Yokocho", desc: "Dinner at Memory Lane izakayas", image: "https://images.unsplash.com/photo-1554797589-7241bb691973?w=600&q=80", price: "RM 60–120", details: "A narrow alley of tiny yakitori and ramen joints near Shinjuku Station. Atmospheric and great for solo or couple dining. Cash only at most stalls.", mapsLink: "https://maps.google.com/?q=Omoide+Yokocho+Shinjuku" },
    ],
  },
  {
    day: 2,
    title: "Culture & Nature",
    activities: [
      { time: "8:00 AM", location: "Meiji Shrine", desc: "Morning walk through the shrine forest", image: "https://images.unsplash.com/photo-1583766395091-2eb9f4040d20?w=600&q=80", price: "Free", details: "A serene Shinto shrine surrounded by a dense forest in central Tokyo. Arrive early to avoid crowds and witness morning rituals.", mapsLink: "https://maps.google.com/?q=Meiji+Shrine+Tokyo" },
      { time: "11:00 AM", location: "Harajuku & Takeshita St", desc: "Street fashion & crêpes", image: "https://images.unsplash.com/photo-1532236204992-f5e85c024202?w=600&q=80", price: "RM 30–80", details: "Harajuku's famous pedestrian street packed with quirky fashion boutiques, crêpe shops, and pop culture stores. Great for souvenirs.", mapsLink: "https://maps.google.com/?q=Takeshita+Street+Tokyo" },
      { time: "2:00 PM", location: "Shinjuku Gyoen", desc: "Beautiful Japanese garden", image: "https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=600&q=80", price: "RM 10", details: "One of Tokyo's largest and most beautiful parks with Japanese, English, and French-style gardens. Perfect for a peaceful afternoon stroll.", mapsLink: "https://maps.google.com/?q=Shinjuku+Gyoen", bookingUrl: "https://example.com/gyoen", bookingLabel: "Buy Tickets" },
      { time: "6:00 PM", location: "Golden Gai", desc: "Bar-hopping in tiny themed bars", image: "https://images.unsplash.com/photo-1551641506-ee5bf4cb45f1?w=600&q=80", price: "RM 50–150", details: "A maze of over 200 tiny bars, each seating only 5-10 people. Many have unique themes. Some charge a small seating fee (¥500-1000).", mapsLink: "https://maps.google.com/?q=Golden+Gai+Shinjuku" },
    ],
  },
  {
    day: 3,
    title: "Day Trip – Hakone",
    activities: [
      { time: "7:30 AM", location: "Shinjuku Station", desc: "Take Romance Car to Hakone", image: "https://images.unsplash.com/photo-1474302770737-173ee21bab63?w=600&q=80", price: "RM 60", details: "The Odakyu Romance Car is a scenic limited-express train. Book window seats on the left side for the best views. Journey takes ~85 minutes.", mapsLink: "https://maps.google.com/?q=Shinjuku+Station", bookingUrl: "https://example.com/romancecar", bookingLabel: "Book Train" },
      { time: "10:00 AM", location: "Hakone Open-Air Museum", desc: "Stunning outdoor sculptures", image: "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=600&q=80", price: "RM 35", details: "Japan's first open-air museum featuring works by Picasso, Henry Moore, and more. The Picasso Pavilion and foot bath are highlights.", mapsLink: "https://maps.google.com/?q=Hakone+Open+Air+Museum", bookingUrl: "https://example.com/museum", bookingLabel: "Buy Tickets" },
      { time: "1:00 PM", location: "Lake Ashi", desc: "Pirate ship cruise with Mt. Fuji views", image: "https://images.unsplash.com/photo-1490806843957-31f4c9a91c65?w=600&q=80", price: "RM 25", details: "A scenic lake cruise on replica pirate ships. On clear days, Mt. Fuji is visible. The cruise takes about 30 minutes one way.", mapsLink: "https://maps.google.com/?q=Lake+Ashi+Hakone", bookingUrl: "https://example.com/cruise", bookingLabel: "Book Cruise" },
      { time: "5:00 PM", location: "Onsen", desc: "Relax in natural hot springs", image: "https://images.unsplash.com/photo-1545569341-9eb8b30979d9?w=600&q=80", price: "RM 40–80", details: "Hakone is famous for its natural hot springs. Many ryokans offer day-use onsen. Remember: tattoos may be restricted at some facilities.", mapsLink: "https://maps.google.com/?q=Hakone+Onsen", bookingUrl: "https://example.com/onsen", bookingLabel: "Reserve Onsen" },
    ],
  },
  {
    day: 4,
    title: "Asakusa & Akihabara",
    activities: [
      { time: "9:00 AM", location: "Senso-ji Temple", desc: "Tokyo's oldest temple & Nakamise St", image: "https://images.unsplash.com/photo-1526481280693-3bfa7568e0f3?w=600&q=80", price: "Free", details: "Tokyo's oldest and most significant temple. Walk through the iconic Kaminarimon gate and browse Nakamise shopping street for traditional snacks and souvenirs.", mapsLink: "https://maps.google.com/?q=Sensoji+Temple+Tokyo" },
      { time: "12:00 PM", location: "Asakusa", desc: "Local ramen lunch", image: "https://images.unsplash.com/photo-1557872943-16a5ac26437e?w=600&q=80", price: "RM 25–40", details: "Try a bowl at one of the highly-rated local ramen shops. Recommended: Fuunji for tsukemen or Ichiran for classic tonkotsu.", mapsLink: "https://maps.google.com/?q=Asakusa+Tokyo" },
      { time: "2:00 PM", location: "Akihabara", desc: "Anime shops & maid cafés", image: "https://images.unsplash.com/photo-1480796927426-f609979314bd?w=600&q=80", price: "RM 30–200", details: "The electric town and otaku paradise. Visit multi-story arcades, anime merchandise shops, and experience a themed maid café.", mapsLink: "https://maps.google.com/?q=Akihabara+Tokyo" },
      { time: "6:00 PM", location: "Tokyo Skytree", desc: "Sunset views from observation deck", image: "https://images.unsplash.com/photo-1536098561742-ca998e48cbcc?w=600&q=80", price: "RM 50", details: "At 634m, it's the tallest tower in the world. The Tembo Deck (350m) offers stunning 360° views. Visit at sunset for the best experience.", mapsLink: "https://maps.google.com/?q=Tokyo+Skytree", bookingUrl: "https://example.com/skytree", bookingLabel: "Buy Tickets" },
    ],
  },
  {
    day: 5,
    title: "Shopping & Departure",
    activities: [
      { time: "9:00 AM", location: "Ginza", desc: "Premium shopping district", image: "https://images.unsplash.com/photo-1573455494060-c5595004fb6c?w=600&q=80", price: "Varies", details: "Tokyo's upscale shopping district. Visit the flagship Uniqlo, MUJI, and department stores like Mitsukoshi. Tax-free shopping available for tourists.", mapsLink: "https://maps.google.com/?q=Ginza+Tokyo" },
      { time: "12:00 PM", location: "Ramen Street", desc: "Farewell ramen bowl", image: "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=600&q=80", price: "RM 25–35", details: "Located in Tokyo Station's underground, Ramen Street features 8 of Japan's top ramen shops. A perfect last meal before departure.", mapsLink: "https://maps.google.com/?q=Tokyo+Ramen+Street" },
      { time: "2:00 PM", location: "Hotel → Airport", desc: "Check out & head to Narita", image: "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=600&q=80", price: "RM 30 (train)", details: "Allow at least 90 minutes for the train to Narita Airport. Buy last-minute souvenirs at the airport's extensive shopping area.", mapsLink: "https://maps.google.com/?q=Narita+Airport" },
    ],
  },
];

const BUDGET = [
  { category: "✈️ Flights", amount: 1200 },
  { category: "🏨 Hotel (4 nights)", amount: 1000 },
  { category: "🍜 Food & Dining", amount: 400 },
  { category: "🎫 Activities", amount: 250 },
  { category: "🚃 Transport", amount: 150 },
];

interface ItineraryDisplayProps {
  itinerary: any;
  onRegenerate: () => void;
  onEditPreferences: () => void;
}

/**
 * ActivityCard Component
 * Displays an individual activity or meal in the daily itinerary.
 * Uses a Collapsible component to show/hide detailed information.
 */
const ActivityCard = ({ act }: { act: Activity }) => {
  const [open, setOpen] = useState(false);

  return (
    <Collapsible open={open} onOpenChange={setOpen}>
      <div className="relative bg-background rounded-xl border border-border hover:border-primary/30 transition-colors overflow-hidden">
        <div className="absolute -left-[31px] top-5 w-3 h-3 rounded-full bg-primary border-2 border-card" />
        <CollapsibleTrigger className="w-full text-left p-4 flex items-start justify-between gap-3 cursor-pointer">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
              <Clock className="h-3 w-3 shrink-0" />
              {act.time}
              {act.price && (
                <>
                  <span className="text-border">•</span>
                  <DollarSign className="h-3 w-3 shrink-0" />
                  <span className="font-medium text-primary">{act.price}</span>
                </>
              )}
            </div>
            <div className="flex items-center gap-2 font-medium text-sm text-card-foreground">
              <MapPin className="h-3.5 w-3.5 text-primary shrink-0" />
              <span className="truncate">{act.location}</span>
            </div>
            <p className="text-sm text-muted-foreground mt-1">{act.desc}</p>
          </div>
          <ChevronDown className={`h-4 w-4 text-muted-foreground shrink-0 mt-1 transition-transform duration-200 ${open ? "rotate-180" : ""}`} />
        </CollapsibleTrigger>

        <CollapsibleContent>
          <div className="px-4 pb-4 space-y-3">
            <div className="rounded-lg overflow-hidden border border-border">
              <img src={act.image} alt={act.location} className="w-full h-40 object-cover" loading="lazy" />
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed">{act.details}</p>
            <div className="flex flex-wrap gap-2">
              <Button variant="outline" size="sm" className="rounded-lg text-xs" asChild>
                <a href={act.mapsLink} target="_blank" rel="noopener noreferrer">
                  <MapPin className="mr-1.5 h-3 w-3" />
                  View on Maps
                  <ExternalLink className="ml-1 h-3 w-3" />
                </a>
              </Button>
              {act.bookingUrl && (
                <Button size="sm" className="rounded-lg text-xs" asChild>
                  <a href={act.bookingUrl} target="_blank" rel="noopener noreferrer">
                    <Ticket className="mr-1.5 h-3 w-3" />
                    {act.bookingLabel || "Book Now"}
                    <ExternalLink className="ml-1 h-3 w-3" />
                  </a>
                </Button>
              )}
            </div>
          </div>
        </CollapsibleContent>
      </div>
    </Collapsible>
  );
};

const FlightCard = ({ flight, type }: { flight: any, type: "outbound" | "return" }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="bg-card rounded-xl border border-border overflow-hidden transition-all hover:shadow-md mb-3 font-sans">
      {/* Top Header Section */}
      <div 
        className="p-4 flex items-center justify-between cursor-pointer hover:bg-muted/50"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex items-center gap-4 flex-1">
          <div className="w-8 h-8 flex-shrink-0 flex items-center justify-center bg-white rounded-full p-1 overflow-hidden border border-border shadow-sm">
            {flight.airline_logo ? (
              <img src={flight.airline_logo} alt={flight.airline} className="w-full h-full object-contain" />
            ) : (
              <Plane className="w-5 h-5 text-muted-foreground" />
            )}
          </div>
          
          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-foreground">
                {type === "outbound" ? "Departure" : "Return"} • {flight.departure_date || "Sun, Apr 5"}
              </span>
            </div>
            <div className="flex items-center gap-2 mt-1">
              <div className="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 text-[10px] font-medium border border-emerald-100">
                Avoids as much CO2e as 731 trees absorb in a day
              </div>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-6">
          <div className="text-right">
            <div className="text-[11px] text-muted-foreground uppercase tracking-wide">39 kg CO2e</div>
            <div className="text-[10px] text-emerald-600 font-medium">-24% emissions</div>
          </div>
          
          <Button 
            size="sm" 
            className="bg-primary hover:bg-primary/90 text-primary-foreground font-medium rounded-full px-4 h-8 text-xs shadow-sm"
            onClick={(e) => {
              e.stopPropagation();
              window.open(flight.booking_url, "_blank", "noopener,noreferrer");
            }}
          >
            Select flight
          </Button>

          <div className="text-right min-w-[80px]">
            <div className="text-base font-medium text-emerald-600">RM {flight.price}</div>
            <div className="text-[10px] text-muted-foreground">round trip</div>
          </div>
          
          <ChevronDown className={cn("h-5 w-5 text-muted-foreground transition-transform", isOpen && "rotate-180")} />
        </div>
      </div>

      {/* Collapsible Content - Leg Details */}
      <Collapsible open={isOpen}>
        <CollapsibleContent>
          <div className="px-4 pb-6 pt-4 border-t border-border bg-muted/20">
            <div className="space-y-8">
              {flight.legs?.map((leg: any, idx: number) => (
                <div key={idx} className="relative pl-10">
                  {/* Dots and dashed line */}
                  <div className="absolute left-4 top-1.5 bottom-1.5 w-[2px] border-l-2 border-dotted border-muted-foreground/30" />
                  <div className="absolute left-[13px] top-1 w-2.5 h-2.5 rounded-full border-2 border-muted-foreground bg-card" />
                  <div className="absolute left-[13px] bottom-1 w-2.5 h-2.5 rounded-full border-2 border-muted-foreground bg-card" />
                  
                  <div className="flex justify-between">
                    <div className="space-y-4">
                      <div className="text-sm text-foreground flex items-center gap-2">
                        <span className="font-medium">{leg.departure_time}</span>
                        <span>•</span>
                        <span>{leg.departure_airport} ({leg.departure_iata})</span>
                      </div>
                      
                      <div className="text-xs text-muted-foreground">
                        Travel time: {leg.duration}
                      </div>
                      
                      <div className="text-sm text-foreground flex items-center gap-2">
                        <span className="font-medium">{leg.arrival_time}</span>
                        <span>•</span>
                        <span>{leg.arrival_airport} ({leg.arrival_iata})</span>
                      </div>

                      <div className="text-[11px] text-muted-foreground mt-4 flex items-center gap-3">
                        <span>{leg.airline}</span>
                        <span>•</span>
                        <span>Economy</span>
                        <span>•</span>
                        <span>Airbus A321neo</span>
                        <span>•</span>
                        <span>{leg.flight_number}</span>
                      </div>
                    </div>

                    <div className="text-right space-y-2">
                      <div className="flex items-center justify-end gap-2 text-[11px] text-muted-foreground">
                        <span>Below average legroom (28 in)</span>
                        <Plane className="h-3 w-3 rotate-90" />
                      </div>
                      <div className="flex items-center justify-end gap-2 text-[11px] text-muted-foreground">
                        <span>In-seat USB outlet</span>
                        <DollarSign className="h-3 w-3" />
                      </div>
                      <div className="flex items-center justify-end gap-2 text-[11px] text-muted-foreground">
                        <span>Emissions estimate: 39 kg CO2e</span>
                      </div>
                    </div>
                  </div>
                  
                  {/* Layover Section */}
                  {idx < flight.legs.length - 1 && (
                    <div className="ml-[-10px] my-6 py-3 border-y border-border text-xs font-medium text-foreground bg-muted/40 px-3 rounded-md">
                      {leg.layover_duration || "1 hr 30 min"} layover • {leg.arrival_airport} ({leg.arrival_iata})
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </CollapsibleContent>
      </Collapsible>
    </div>
  );
};

/**
 * ItineraryDisplay Component
 * The main results view that displays the generated travel plan.
 * Shows selected flights, hotel, daily schedule, and budget breakdown.
 */
const ItineraryDisplay = ({ itinerary, onRegenerate, onEditPreferences }: ItineraryDisplayProps) => {
  // Use real data from the backend or fallback to mock data for demonstration
  const displayItinerary = itinerary?.days || MOCK_ITINERARY;
  const budgetSummary = itinerary?.budget_summary || BUDGET;
  const total = itinerary?.total_budget || 0;
  const hotel = itinerary?.hotel;
  const outboundFlights = itinerary?.flights?.outbound || [];
  const returnFlights = itinerary?.flights?.return || [];

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-wrap gap-3">
        <Button variant="outline" onClick={onRegenerate} className="rounded-xl">
          <RefreshCw className="mr-2 h-4 w-4" />
          Regenerate Plan
        </Button>
        <Button variant="outline" onClick={onEditPreferences} className="rounded-xl">
          <Settings2 className="mr-2 h-4 w-4" />
          Edit Preferences
        </Button>
      </div>

      {/* Hotel Recommendation Section */}
      {hotel && (
        <div className="bg-card rounded-2xl shadow-sm border border-border overflow-hidden">
          <div className="p-6 md:p-8">
            <h2 className="text-xl font-semibold mb-6 text-card-foreground flex items-center gap-2">
              <Hotel className="h-5 w-5 text-primary" />
              Recommended Stay
            </h2>
            
            <div className="flex flex-col md:flex-row gap-6">
              <div className="w-full md:w-1/3 rounded-xl overflow-hidden border border-border aspect-video md:aspect-square">
                <img 
                  src={hotel.image} 
                  alt={hotel.name} 
                  className="w-full h-full object-cover"
                />
              </div>
              
              <div className="flex-1 space-y-4">
                <div>
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <h3 className="text-lg font-bold text-card-foreground">{hotel.name}</h3>
                    <div className="flex items-center gap-1 text-yellow-500">
                      <Star className="h-4 w-4 fill-current" />
                      <span className="text-sm font-medium">{hotel.rating || "4.5"}</span>
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {hotel.description}
                  </p>
                </div>

                <div className="flex flex-wrap items-center gap-4 text-sm">
                  <div className="flex items-center gap-1.5 text-card-foreground font-medium">
                    <DollarSign className="h-4 w-4 text-primary" />
                    {hotel.price}
                  </div>
                </div>

                <div className="flex flex-wrap gap-3 pt-2">
                  <Button className="rounded-xl px-6" asChild>
                    <a href={hotel.booking_url} target="_blank" rel="noopener noreferrer">
                      <Ticket className="mr-2 h-4 w-4" />
                      Book Now
                      <ExternalLink className="ml-2 h-3.5 w-3.5" />
                    </a>
                  </Button>
                  <Button variant="outline" className="rounded-xl" asChild>
                    <a href={hotel.maps_url} target="_blank" rel="noopener noreferrer">
                      <MapPin className="mr-2 h-4 w-4" />
                      View on Maps
                    </a>
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Flights Section */}
      {outboundFlights.length > 0 ? (
        <div className="bg-card rounded-2xl shadow-sm border border-border p-6 md:p-8">
          <h2 className="text-xl font-semibold mb-6 text-card-foreground flex items-center gap-2">
            <Plane className="h-5 w-5 text-primary" />
            Top departing options
          </h2>
          
          <div className="space-y-4">
            {outboundFlights.map((f: any, i: number) => (
              <FlightCard key={i} flight={f} type="outbound" />
            ))}
          </div>
        </div>
      ) : (
        <div className="bg-card rounded-2xl shadow-sm border border-border p-6 md:p-8 text-center">
          <Plane className="h-8 w-8 text-muted-foreground mx-auto mb-2 opacity-50" />
          <p className="text-sm text-muted-foreground">No flight options available for this route/dates.</p>
        </div>
      )}

      <div className="bg-card rounded-2xl shadow-sm border border-border p-6 md:p-8">
        <h2 className="text-xl font-semibold mb-6 text-card-foreground">
          📅 Your Travel Itinerary
        </h2>
        <div className="space-y-8">
          {displayItinerary.map((day: any) => (
            <div key={day.day}>
              <div className="flex items-center gap-3 mb-4">
                <span className="inline-flex items-center justify-center w-9 h-9 rounded-full bg-primary text-primary-foreground text-sm font-bold">
                  {day.day}
                </span>
                <h3 className="text-lg font-semibold text-card-foreground">
                  Day {day.day}: {day.title}
                </h3>
              </div>
              <div className="ml-4 border-l-2 border-border pl-6 space-y-4">
                {day.activities.map((act: any, i: number) => (
                  <ActivityCard key={i} act={act} />
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-card rounded-2xl shadow-sm border border-border p-6 md:p-8">
        <h2 className="text-xl font-semibold mb-4 text-card-foreground">💰 Budget Summary</h2>
        <div className="space-y-3">
          {budgetSummary.map((item: any) => (
            <div key={item.category} className="flex justify-between items-center py-2 border-b border-border last:border-0">
              <span className="text-sm text-card-foreground">{item.category}</span>
              <span className="text-sm font-semibold text-card-foreground">RM {item.amount.toLocaleString()}</span>
            </div>
          ))}
          <div className="flex justify-between items-center pt-3">
            <span className="font-semibold text-card-foreground">Total</span>
            <span className="text-lg font-bold text-primary">RM {total.toLocaleString()}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ItineraryDisplay;
