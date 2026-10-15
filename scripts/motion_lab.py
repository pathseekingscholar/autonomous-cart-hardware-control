from __future__ import annotations

import argparse

from cart_stack.shared.models import MotionModelInput
from cart_stack.shared.physics import MPH_TO_MPS, calculate_motion_model


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Print motion-model estimates for the shopping cart."
    )
    parser.add_argument("--mass-kg", type=float, default=24.0, help="Total cart mass in kg.")
    parser.add_argument(
        "--track-width-m",
        type=float,
        default=0.58,
        help="Left-to-right wheel separation in meters.",
    )
    parser.add_argument(
        "--max-linear-speed-mps",
        type=float,
        default=0.9,
        help="Estimated top linear speed in meters/second.",
    )
    parser.add_argument(
        "--zero-to-max-speed-s",
        type=float,
        default=2.8,
        help="Measured time to go from rest to max speed in seconds.",
    )
    parser.add_argument(
        "--cruise-speed-mph",
        type=float,
        default=1.4,
        help="Chosen forward speed in mph for the moving-turn estimate.",
    )
    parser.add_argument(
        "--turn-angle-deg",
        type=float,
        default=90.0,
        help="Turn angle to evaluate in degrees.",
    )
    parser.add_argument(
        "--mph-step",
        type=float,
        default=0.25,
        help="Step size for the turn-time sweep table in mph.",
    )
    return parser


def format_seconds(value: float | None) -> str:
    return "inf" if value is None else f"{value:.3f} s"


def speed_range(max_linear_speed_mps: float, mph_step: float) -> list[float]:
    max_mph = max_linear_speed_mps / MPH_TO_MPS
    speeds: list[float] = []
    current = 0.0
    while current < max_mph:
        speeds.append(round(current, 3))
        current += mph_step
    speeds.append(round(max_mph, 3))
    return speeds


def main() -> None:
    args = build_parser().parse_args()
    base = MotionModelInput(
        total_mass_kg=args.mass_kg,
        track_width_m=args.track_width_m,
        max_linear_speed_mps=args.max_linear_speed_mps,
        zero_to_max_speed_s=args.zero_to_max_speed_s,
        cruise_speed_mph=args.cruise_speed_mph,
        turn_angle_deg=args.turn_angle_deg,
    )
    result = calculate_motion_model(base)

    print("Shopping Cart Motion Lab")
    print("========================")
    print(f"Mass: {args.mass_kg:.3f} kg")
    print(f"Track width: {args.track_width_m:.3f} m")
    print(f"Top speed: {args.max_linear_speed_mps:.3f} m/s")
    print(f"0 -> max speed time: {args.zero_to_max_speed_s:.3f} s")
    print(f"Cruise speed for moving-turn estimate: {args.cruise_speed_mph:.3f} mph")
    print(f"Turn angle: {args.turn_angle_deg:.1f} deg")
    print()
    print("Summary")
    print("-------")
    print(f"Weight: {result.weight_n:.3f} N ({result.weight_lbf:.3f} lbf)")
    print(f"Average acceleration: {result.average_acceleration_mps2:.3f} m/s^2")
    print(
        "Estimated acceleration at chosen speed: "
        f"{result.estimated_acceleration_at_speed_mps2:.3f} m/s^2"
    )
    print(
        "Spin-in-place angular speed: "
        f"{result.max_angular_speed_spin_rad_s:.3f} rad/s"
    )
    print(
        "Angular speed at chosen forward speed: "
        f"{result.max_angular_speed_at_speed_rad_s:.3f} rad/s"
    )
    print(
        f"Turn time from standstill: {format_seconds(result.standstill_turn_time_s)}"
    )
    print(f"Turn time while moving: {format_seconds(result.moving_turn_time_s)}")
    print(
        "Turn radius at chosen speed: "
        + ("inf" if result.turn_radius_m is None else f"{result.turn_radius_m:.3f} m")
    )
    print()
    print("Turn-Time Sweep")
    print("---------------")
    print("speed_mph | turn_time_s | angular_speed_rad_s")
    for mph in speed_range(args.max_linear_speed_mps, args.mph_step):
        sweep = calculate_motion_model(base.model_copy(update={"cruise_speed_mph": mph}))
        print(
            f"{mph:8.3f} | "
            f"{format_seconds(sweep.moving_turn_time_s):>11} | "
            f"{sweep.max_angular_speed_at_speed_rad_s:19.3f}"
        )
    print()
    print("Notes")
    print("-----")
    for note in result.notes:
        print(f"- {note}")


if __name__ == "__main__":
    main()
