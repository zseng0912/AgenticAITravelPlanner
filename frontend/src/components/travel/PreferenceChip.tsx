import { cn } from "@/lib/utils";

interface PreferenceChipProps {
  label: string;
  icon: string;
  selected: boolean;
  onClick: () => void;
}

const PreferenceChip = ({ label, icon, selected, onClick }: PreferenceChipProps) => (
  <button
    type="button"
    onClick={onClick}
    className={cn(
      "inline-flex items-center gap-2 px-4 py-2 rounded-full border text-sm font-medium transition-all duration-200",
      selected ? "chip-active shadow-sm" : "chip-inactive"
    )}
  >
    <span>{icon}</span>
    {label}
  </button>
);

export default PreferenceChip;
