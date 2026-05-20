from dataclasses import dataclass, field
from heapq import heappop, heappush
from itertools import count
from typing import Dict, List, Optional


PRIORITY_LEVELS = {
    "emergency": 1,
    "critical": 2,
    "normal": 3,
}


@dataclass(order=True)
class QueueEntry:
    priority: int
    arrival_order: int
    patient_id: int = field(compare=False)


@dataclass
class Patient:
    patient_id: int
    name: str
    age: int
    condition: str
    priority_label: str
    active_arrival_order: int
    is_waiting: bool = True


class HospitalQueue:
    def __init__(self) -> None:
        self._queue: List[QueueEntry] = []
        self._patients: Dict[int, Patient] = {}
        self._arrival_counter = count(1)
        self._patient_counter = count(101)

    def add_patient(self, name: str, age: int, condition: str, priority_label: str) -> Patient:
        priority_label = priority_label.strip().lower()
        if priority_label not in PRIORITY_LEVELS:
            allowed = ", ".join(PRIORITY_LEVELS)
            raise ValueError(f"Unknown priority. Use one of: {allowed}")

        patient_id = next(self._patient_counter)
        arrival_order = next(self._arrival_counter)
        patient = Patient(
            patient_id=patient_id,
            name=name.strip(),
            age=age,
            condition=condition.strip(),
            priority_label=priority_label,
            active_arrival_order=arrival_order,
        )

        self._patients[patient_id] = patient
        heappush(
            self._queue,
            QueueEntry(PRIORITY_LEVELS[priority_label], arrival_order, patient_id),
        )
        return patient

    def serve_next_patient(self) -> Optional[Patient]:
        while self._queue:
            entry = heappop(self._queue)
            patient = self._patients[entry.patient_id]
            if self._is_active_entry(entry, patient):
                patient.is_waiting = False
                return patient
        return None

    def peek_next_patient(self) -> Optional[Patient]:
        while self._queue:
            entry = self._queue[0]
            patient = self._patients[entry.patient_id]
            if self._is_active_entry(entry, patient):
                return patient
            heappop(self._queue)
        return None

    def change_priority(self, patient_id: int, new_priority_label: str) -> Patient:
        new_priority_label = new_priority_label.strip().lower()
        if new_priority_label not in PRIORITY_LEVELS:
            allowed = ", ".join(PRIORITY_LEVELS)
            raise ValueError(f"Unknown priority. Use one of: {allowed}")

        patient = self._patients.get(patient_id)
        if patient is None:
            raise ValueError("Patient ID does not exist.")
        if not patient.is_waiting:
            raise ValueError("Cannot update priority after the patient has been served.")

        patient.priority_label = new_priority_label
        patient.active_arrival_order = next(self._arrival_counter)
        heappush(
            self._queue,
            QueueEntry(PRIORITY_LEVELS[new_priority_label], patient.active_arrival_order, patient_id),
        )
        return patient

    def waiting_patients(self) -> List[Patient]:
        return sorted(
            (patient for patient in self._patients.values() if patient.is_waiting),
            key=lambda patient: (
                PRIORITY_LEVELS[patient.priority_label],
                patient.active_arrival_order,
            ),
        )

    def _is_active_entry(self, entry: QueueEntry, patient: Patient) -> bool:
        return (
            patient.is_waiting
            and entry.priority == PRIORITY_LEVELS[patient.priority_label]
            and entry.arrival_order == patient.active_arrival_order
        )


def print_patient(patient: Patient) -> None:
    print(
        f"ID: {patient.patient_id} | Name: {patient.name} | Age: {patient.age} | "
        f"Priority: {patient.priority_label.title()} | Condition: {patient.condition}"
    )


def read_priority() -> str:
    print("Priority levels: emergency, critical, normal")
    return input("Enter priority: ")


def add_patient_flow(queue: HospitalQueue) -> None:
    name = input("Patient name: ")
    age = int(input("Patient age: "))
    condition = input("Medical condition: ")
    priority = read_priority()
    patient = queue.add_patient(name, age, condition, priority)
    print("\nPatient added successfully.")
    print_patient(patient)


def serve_patient_flow(queue: HospitalQueue) -> None:
    patient = queue.serve_next_patient()
    if patient is None:
        print("\nNo patients are waiting.")
        return

    print("\nServing patient:")
    print_patient(patient)


def peek_patient_flow(queue: HospitalQueue) -> None:
    patient = queue.peek_next_patient()
    if patient is None:
        print("\nNo patients are waiting.")
        return

    print("\nNext patient to be served:")
    print_patient(patient)


def list_waiting_flow(queue: HospitalQueue) -> None:
    patients = queue.waiting_patients()
    if not patients:
        print("\nNo patients are waiting.")
        return

    print("\nWaiting patients by priority:")
    for patient in patients:
        print_patient(patient)


def change_priority_flow(queue: HospitalQueue) -> None:
    patient_id = int(input("Patient ID: "))
    new_priority = read_priority()
    patient = queue.change_priority(patient_id, new_priority)
    print("\nPriority updated successfully.")
    print_patient(patient)


def seed_demo_data(queue: HospitalQueue) -> None:
    queue.add_patient("Bhumi Ojha", 21, "Chest pain", "critical")
    queue.add_patient("Debopriyo Maity", 20, "Routine fever", "normal")
    queue.add_patient("Devesh Sureka", 19, "Accident trauma", "emergency")
    queue.add_patient("Amisa Agarwal", 19, "Breathing difficulty", "emergency")


def run_demo() -> None:
    queue = HospitalQueue()
    seed_demo_data(queue)

    print("Initial queue:")
    list_waiting_flow(queue)

    print("\nTreatment order:")
    while True:
        patient = queue.serve_next_patient()
        if patient is None:
            break
        print_patient(patient)


def run_menu() -> None:
    queue = HospitalQueue()

    menu = """
Hospital Queue Management System
1. Add patient
2. Serve next patient
3. View next patient
4. List waiting patients
5. Change patient priority
6. Load demo data
0. Exit
"""

    actions = {
        "1": add_patient_flow,
        "2": serve_patient_flow,
        "3": peek_patient_flow,
        "4": list_waiting_flow,
        "5": change_priority_flow,
        "6": lambda q: seed_demo_data(q),
    }

    while True:
        print(menu)
        choice = input("Choose an option: ").strip()
        if choice == "0":
            print("Goodbye.")
            break

        action = actions.get(choice)
        if action is None:
            print("Invalid choice. Please try again.")
            continue

        try:
            action(queue)
        except ValueError as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Hospital Queue Management System")
    parser.add_argument("--demo", action="store_true", help="run a non-interactive demo")
    args = parser.parse_args()

    if args.demo:
        run_demo()
    else:
        run_menu()