#!/usr/bin/env python3
"""
Probe or restart Reachy's mobile-base user service over SSH.

The helper is intentionally small and machine-readable so Unity can run it in
the background and parse one JSON object from stdout.
"""

from __future__ import annotations

import argparse
import json
import shlex
import sys
import time


DEFAULT_SERVICE_NAME = "reachy_mobile_base.service"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe/restart Reachy mobile-base service over SSH.")
    parser.add_argument("--action", choices=("probe", "restart"), required=True)
    parser.add_argument("--reachy-host", required=True)
    parser.add_argument("--reachy-user", default="reachy")
    parser.add_argument("--reachy-password", default="")
    parser.add_argument("--service-name", default=DEFAULT_SERVICE_NAME)
    parser.add_argument("--ssh-timeout-seconds", type=float, default=10.0)
    parser.add_argument("--restart-wait-seconds", type=float, default=12.0)
    parser.add_argument("--journal-lines", type=int, default=12)
    return parser.parse_args()


def emit_json(payload: dict, exit_code: int) -> int:
    sys.stdout.write(json.dumps(payload, ensure_ascii=True))
    sys.stdout.flush()
    return exit_code


def compact_text(text: str, max_chars: int = 1200) -> str:
    raw = str(text or "").replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in raw.split("\n") if line.strip()]
    compact = " | ".join(lines)
    if len(compact) <= max_chars:
        return compact
    return compact[: max_chars - 3].rstrip() + "..."


def shell_wrap(command_text: str) -> str:
    return "bash -lc " + shlex.quote(command_text)


def ssh_connect(host: str, user: str, password: str, timeout_seconds: float):
    try:
        import paramiko  # type: ignore
    except Exception as exc:
        raise RuntimeError(
            "paramiko is unavailable in the local helper environment. Install requirements-optional.txt first."
        ) from exc

    timeout = max(3.0, float(timeout_seconds))
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=host,
        port=22,
        username=user,
        password=password or None,
        timeout=timeout,
        banner_timeout=timeout,
        auth_timeout=timeout,
        look_for_keys=True,
        allow_agent=True,
    )
    return client


def run_remote_command(client, command_text: str, timeout_seconds: float) -> tuple[int, str, str]:
    stdin, stdout, stderr = client.exec_command(command_text, timeout=max(3.0, float(timeout_seconds)))
    if stdin is not None:
        stdin.close()
    output = stdout.read().decode("utf-8", errors="replace")
    error_text = stderr.read().decode("utf-8", errors="replace")
    exit_status = stdout.channel.recv_exit_status()
    return exit_status, output, error_text


def bool_from_process_listing(output: str) -> tuple[bool, str]:
    compact = compact_text(output, max_chars=240)
    return bool(compact), compact


def build_process_probe_command(*needles: str) -> str:
    serialized_needles = json.dumps([str(needle or "") for needle in needles if str(needle or "")])
    script = f"""python3 - <<'PY'
import json
import subprocess

needles = json.loads({json.dumps(serialized_needles)})
matches = []
for raw_line in subprocess.check_output(["ps", "-eo", "pid=,args="], text=True).splitlines():
    line = raw_line.strip()
    if not line:
        continue
    parts = line.split(None, 1)
    if len(parts) != 2:
        continue
    _pid_text, args = parts
    if "python3 - <<'PY'" in args:
        continue
    if any(needle and needle in args for needle in needles):
        matches.append(line)
print("\\n".join(matches[:3]))
PY"""
    return shell_wrap(script)


def collect_service_state(client, service_name: str, ssh_timeout_seconds: float, journal_lines: int) -> dict:
    service_quoted = shlex.quote(service_name)

    service_status_exit, service_status_out, service_status_err = run_remote_command(
        client,
        shell_wrap(f"systemctl --user is-active {service_quoted}"),
        timeout_seconds=ssh_timeout_seconds,
    )
    service_status_text = compact_text(service_status_out or service_status_err, max_chars=120)
    service_active = service_status_exit == 0 and service_status_text.lower() == "active"

    hal_exit, hal_out, hal_err = run_remote_command(
        client,
        build_process_probe_command("zuuu_hal/hal", "zuuu_hal"),
        timeout_seconds=ssh_timeout_seconds,
    )
    hal_process_running, hal_match = bool_from_process_listing(hal_out or hal_err)

    sdk_exit, sdk_out, sdk_err = run_remote_command(
        client,
        build_process_probe_command("mobile_base_sdk_server"),
        timeout_seconds=ssh_timeout_seconds,
    )
    sdk_server_process_running, sdk_match = bool_from_process_listing(sdk_out or sdk_err)

    safe_journal_lines = max(4, min(40, int(journal_lines)))
    journal_exit, journal_out, journal_err = run_remote_command(
        client,
        shell_wrap(
            f"journalctl --user -u {service_quoted} -n {safe_journal_lines} --no-pager -o cat 2>/dev/null || true"
        ),
        timeout_seconds=max(ssh_timeout_seconds, 15.0),
    )
    journal_excerpt = compact_text(journal_out or journal_err, max_chars=640)

    healthy = service_active and hal_process_running and sdk_server_process_running
    missing_parts = []
    if not service_active:
        missing_parts.append("service inactive")
    if not hal_process_running:
        missing_parts.append("zuuu_hal missing")
    if not sdk_server_process_running:
        missing_parts.append("mobile_base_sdk_server missing")

    if healthy:
        message = "Mobile base service healthy."
    else:
        message = "Mobile base service unhealthy: " + ", ".join(missing_parts) + "."

    detail_parts = [
        f"isActive={service_status_text or ('exit-' + str(service_status_exit))}",
        f"halRunning={hal_process_running}",
        f"sdkRunning={sdk_server_process_running}",
    ]
    if hal_match:
        detail_parts.append(f"halMatch={hal_match}")
    if sdk_match:
        detail_parts.append(f"sdkMatch={sdk_match}")
    if journal_excerpt:
        detail_parts.append(f"journal={journal_excerpt}")
    if hal_exit not in (0, 1):
        detail_parts.append(f"halExit={hal_exit}")
    if sdk_exit not in (0, 1):
        detail_parts.append(f"sdkExit={sdk_exit}")
    if journal_exit not in (0, 1):
        detail_parts.append(f"journalExit={journal_exit}")

    return {
        "reachable": True,
        "service_active": service_active,
        "hal_process_running": hal_process_running,
        "sdk_server_process_running": sdk_server_process_running,
        "healthy": healthy,
        "message": message,
        "detail": "; ".join(detail_parts),
    }


def main() -> int:
    args = parse_args()
    action = str(args.action or "probe").strip().lower()
    host = str(args.reachy_host or "").strip()
    user = str(args.reachy_user or "reachy").strip() or "reachy"
    password = str(args.reachy_password or "")
    service_name = str(args.service_name or DEFAULT_SERVICE_NAME).strip() or DEFAULT_SERVICE_NAME
    ssh_timeout_seconds = max(3.0, float(args.ssh_timeout_seconds))
    restart_wait_seconds = max(0.0, float(args.restart_wait_seconds))

    payload = {
        "action": action,
        "ok": False,
        "reachable": False,
        "service_active": False,
        "hal_process_running": False,
        "sdk_server_process_running": False,
        "healthy": False,
        "restart_attempted": False,
        "restart_succeeded": False,
        "host": host,
        "service_name": service_name,
        "message": "",
        "detail": "",
        "error": "",
    }

    if not host:
        payload["error"] = "Missing --reachy-host."
        payload["message"] = "Mobile base helper requires a target host."
        return emit_json(payload, 2)

    client = None
    try:
        client = ssh_connect(host, user, password, ssh_timeout_seconds)
        payload["reachable"] = True

        if action == "restart":
            payload["restart_attempted"] = True
            service_quoted = shlex.quote(service_name)
            restart_exit, restart_out, restart_err = run_remote_command(
                client,
                shell_wrap(f"systemctl --user restart {service_quoted}"),
                timeout_seconds=max(ssh_timeout_seconds, restart_wait_seconds + 10.0),
            )
            restart_error = compact_text(restart_err, max_chars=240)
            restart_output = compact_text(restart_out, max_chars=240)
            if restart_wait_seconds > 0.0:
                time.sleep(restart_wait_seconds)
            state = collect_service_state(
                client,
                service_name=service_name,
                ssh_timeout_seconds=ssh_timeout_seconds,
                journal_lines=args.journal_lines,
            )
            payload.update(state)
            payload["ok"] = True
            payload["restart_succeeded"] = restart_exit == 0 and state["healthy"]
            if restart_exit != 0:
                payload["message"] = f"Mobile base service restart command failed with exit code {restart_exit}."
                payload["error"] = restart_error or restart_output or "systemctl restart failed."
            elif payload["restart_succeeded"]:
                payload["message"] = "Mobile base service restarted and recovered."
            else:
                payload["message"] = "Mobile base service restarted but the base stack is still unhealthy."
                payload["error"] = restart_error
            return emit_json(payload, 0 if payload["restart_succeeded"] else 1)

        state = collect_service_state(
            client,
            service_name=service_name,
            ssh_timeout_seconds=ssh_timeout_seconds,
            journal_lines=args.journal_lines,
        )
        payload.update(state)
        payload["ok"] = True
        return emit_json(payload, 0 if payload["healthy"] else 1)
    except Exception as exc:
        payload["message"] = "Mobile base helper failed."
        payload["error"] = compact_text(str(exc), max_chars=320)
        return emit_json(payload, 1)
    finally:
        if client is not None:
            client.close()


if __name__ == "__main__":
    raise SystemExit(main())
