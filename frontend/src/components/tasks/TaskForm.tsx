import type { TaskCreate } from "../../types/task";

interface TaskFormProps {
  formData: TaskCreate;
  durationHours: number;
  durationMinutesPart: number;
  finishWindowStart: string;
  finishWindowEnd: string;
  finishWindowInvalid: boolean;
  onSubmit: (event: React.FormEvent) => void;
  onNameChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onDurationTotalChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onDurationHoursChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onDurationMinutesPartChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onPreferredTimeChange: (event: React.ChangeEvent<HTMLSelectElement>) => void;
  onSplittableChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onFinishWindowStartChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onFinishWindowEndChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

export function TaskForm({
  formData,
  durationHours,
  durationMinutesPart,
  finishWindowStart,
  finishWindowEnd,
  finishWindowInvalid,
  onSubmit,
  onNameChange,
  onDurationTotalChange,
  onDurationHoursChange,
  onDurationMinutesPartChange,
  onPreferredTimeChange,
  onSplittableChange,
  onFinishWindowStartChange,
  onFinishWindowEndChange
}: TaskFormProps) {
  let preferredSelectValue = formData.preferred_time_of_day;
  if (preferredSelectValue === undefined || preferredSelectValue === null) {
    preferredSelectValue = "anytime";
  }

  let dateRangeError = null;
  if (finishWindowInvalid) {
    dateRangeError = (
      <p className="task-form-error">Finish window end must be on or after start.</p>
    );
  }

  return (
    <form className="task-form" onSubmit={onSubmit}>
      <input
        type="text"
        placeholder="Task name"
        value={formData.name}
        onChange={onNameChange}
        required
      />

      <label className="task-duration-label">
        Estimated length
        <div className="task-duration-inputs">
          <input
            type="number"
            min={0}
            value={durationHours}
            onChange={onDurationHoursChange}
            aria-label="Estimated duration hours"
          />
          <span>hr</span>
          <input
            type="number"
            min={0}
            max={59}
            value={durationMinutesPart}
            onChange={onDurationMinutesPartChange}
            aria-label="Estimated duration minutes"
          />
          <span>min</span>
        </div>
      </label>

      <input
        type="number"
        min={1}
        placeholder="Total duration (min)"
        value={formData.estimated_duration_minutes}
        onChange={onDurationTotalChange}
        aria-label="Total estimated duration minutes"
      />

      <label className="task-time-pref-label">
        Preferred time of day
        <select value={preferredSelectValue} onChange={onPreferredTimeChange}>
          <option value="anytime">Anytime</option>
          <option value="morning">Morning</option>
          <option value="afternoon">Afternoon</option>
          <option value="evening">Evening</option>
        </select>
      </label>

      <label>
        <input type="checkbox" checked={formData.splittable} onChange={onSplittableChange} />
        Splittable
      </label>

      <label className="task-date-range-label">
        Finish window
        <div className="task-date-range-inputs">
          <input
            type="date"
            value={finishWindowStart}
            onChange={onFinishWindowStartChange}
            aria-label="Finish window start date"
          />
          <span>to</span>
          <input
            type="date"
            value={finishWindowEnd}
            onChange={onFinishWindowEndChange}
            aria-label="Finish window end date"
          />
        </div>
      </label>

      {dateRangeError}

      <button type="submit">Create</button>
    </form>
  );
}
