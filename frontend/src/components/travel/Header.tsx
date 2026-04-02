import { Plane } from "lucide-react";

const Header = () => (
  <header className="py-8 text-center">
    <div className="flex items-center justify-center gap-3 mb-2">
      <div className="p-2 rounded-xl bg-primary/10">
        <Plane className="h-7 w-7 text-primary" />
      </div>
      <h1 className="text-3xl font-bold tracking-tight text-foreground">
        AI Travel Planner
      </h1>
    </div>
    <p className="text-muted-foreground text-lg">
      Plan your perfect trip with AI
    </p>
  </header>
);

export default Header;
