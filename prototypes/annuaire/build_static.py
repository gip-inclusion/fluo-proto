"""Render the annuaire proto to a static site for GitHub Pages.

GitHub Pages only serves static files, so this script renders directory.html
with all the seed data baked in (search and filters run client-side, see the
JS in directory.html) and rewrites absolute asset/link paths to relative ones.

Usage (from prototypes/annuaire/):
    pip install jinja2
    python build_static.py            # writes ./dist/

Only depends on Jinja2 — no database, FastAPI or SQLModel needed.
"""

import ast
import importlib.util
import re
import shutil
from datetime import date, timedelta
from pathlib import Path
from types import SimpleNamespace

from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).parent
WEB = ROOT / "web"
DIST = ROOT / "dist"

_SLOT_POOL = ["09:00", "09:30", "10:00", "11:00", "11:30", "14:00", "14:30", "15:30", "16:30", "17:00"]


def _load_config():
    spec = importlib.util.spec_from_file_location("annuaire_config", WEB / "config.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_seed_lists():
    """Extract the STRUCTURES / PROFESSIONALS literals from seed.py (no imports)."""
    source = (WEB / "seed.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    data = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id in ("STRUCTURES", "PROFESSIONALS"):
                data[target.id] = ast.literal_eval(node.value)
    return data["STRUCTURES"], data["PROFESSIONALS"]


def _contact_means(obj, labels):
    means = []
    for key in ("phone", "email", "form", "agenda"):
        available = getattr(obj, key, None) if key in ("phone", "email") else getattr(obj, f"has_{key}", False)
        if available:
            label, icon = labels[key]
            means.append({"key": key, "label": label, "icon": icon})
    return means


def _week_slots(prof, weekdays):
    if not prof.has_agenda:
        return []
    monday = date.today() - timedelta(days=date.today().weekday())
    days = []
    for offset, weekday in enumerate(weekdays):
        day = monday + timedelta(days=offset)
        seed = (prof.id or 0) * 7 + offset
        if seed % 5 == 2:
            slots = []
        else:
            slots = [_SLOT_POOL[i] for i in range(len(_SLOT_POOL)) if (i + seed) % 3 == 0][:3]
        days.append({"weekday": weekday, "day_label": f"{day.day:02d}/{day.month:02d}", "slots": slots})
    return days


def build():
    cfg = _load_config()
    structures_raw, professionals_raw = _load_seed_lists()

    structures = []
    for i, (name, type_, address, city, phone, email, has_form, has_agenda) in enumerate(structures_raw, start=1):
        structures.append(
            SimpleNamespace(
                id=i,
                name=name,
                type=type_,
                address=address,
                city=city,
                phone=phone,
                email=email,
                has_form=has_form,
                has_agenda=has_agenda,
            )
        )
    by_id = {s.id: s for s in structures}
    for s in structures:
        s._means = _contact_means(s, cfg.CONTACT_MEANS_LABELS)

    professionals = []
    for pid, (idx, first, last, role, phone, email, has_form, has_agenda) in enumerate(professionals_raw, start=1):
        p = SimpleNamespace(
            id=pid,
            first_name=first,
            last_name=last,
            role=role,
            structure_id=idx + 1,
            phone=phone,
            email=email,
            has_form=has_form,
            has_agenda=has_agenda,
        )
        p._structure = by_id.get(p.structure_id)
        p._means = _contact_means(p, cfg.CONTACT_MEANS_LABELS)
        p._mean_keys = {m["key"] for m in p._means}
        p._week_slots = _week_slots(p, cfg.WEEKDAYS)
        professionals.append(p)

    contacts_by_structure = {s.id: [] for s in structures}
    for p in professionals:
        contacts_by_structure[p.structure_id].append(p)

    env = Environment(loader=FileSystemLoader(str(WEB / "templates")), autoescape=True)
    env.globals.update(
        {
            "service_name": cfg.SERVICE_NAME,
            "nav_items": cfg.NAV_ITEMS,
            "structure_type_colors": cfg.STRUCTURE_TYPE_COLORS,
            "structure_types": cfg.STRUCTURE_TYPES,
            "contact_means": cfg.CONTACT_MEANS,
            "message_subjects": cfg.MESSAGE_SUBJECTS,
            "rdv_subjects": cfg.RDV_SUBJECTS,
            "rdv_types": cfg.RDV_TYPES,
        }
    )

    def postprocess(html):
        # Absolute paths -> relative + inter-page links, so the site works
        # under https://user.github.io/<repo>/ with no server-side routing.
        html = html.replace('"/static/', '"static/')
        html = re.sub(r'(href|action)="/annuaire"', r'\1="index.html"', html)
        html = html.replace('href="/mon-espace/profil"', 'href="profil.html"')
        return html

    # Annuaire (home)
    directory_html = env.get_template("directory.html").render(
        request=SimpleNamespace(url=SimpleNamespace(path="/annuaire")),
        people=professionals,
        structures=structures,
        all_professionals=professionals,
        contacts_by_structure=contacts_by_structure,
        people_count=len(professionals),
        structures_count=len(structures),
        q="",
        selected_types=[],
        selected_contacts=[],
        active_tab="personnes",
    )

    # Mon espace > Modifier mon profil
    me = next((p for p in professionals if p.id == cfg.CURRENT_PROFESSIONAL_ID), professionals[0])
    profile_html = env.get_template("profile.html").render(
        request=SimpleNamespace(url=SimpleNamespace(path="/mon-espace/profil")),
        me=me,
        structure=me._structure,
        structures=structures,
        share_info_options=cfg.SHARE_INFO_OPTIONS,
        share_audiences=cfg.SHARE_AUDIENCES,
    )

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    (DIST / "index.html").write_text(postprocess(directory_html), encoding="utf-8")
    (DIST / "profil.html").write_text(postprocess(profile_html), encoding="utf-8")
    shutil.copytree(WEB / "static", DIST / "static")
    # Disable Jekyll so folders like vendor/ are served untouched.
    (DIST / ".nojekyll").write_text("", encoding="utf-8")

    print(f"Built static site in {DIST} ({len(professionals)} professionals, {len(structures)} structures).")


if __name__ == "__main__":
    build()
