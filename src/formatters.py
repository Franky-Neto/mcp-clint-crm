from __future__ import annotations

from models.crm import Group, LostStatus, Organization, Origin, Tag, User
from models.contacts import Contact, Deal
from models.account import AccountFields


def _format_value(value) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        if not value:
            return ""
        if isinstance(value[0], dict):
            return ", ".join(v.get("name", str(v)) for v in value)
        return ", ".join(str(v) for v in value)
    if isinstance(value, dict):
        return value.get("name") or str(value)
    return str(value)


def _pagination_header(entity_name: str, count: int, total: int, offset: int) -> str:
    if count < total:
        return f"**Showing {count} of {total} {entity_name}.** Use offset={offset + count} to see next batch.\n"
    return f"**{total} {entity_name} found.**\n"


def _format_extra_fields(item, known_keys: set[str]) -> list[str]:
    """Iterate all fields from model_dump, yielding lines for keys not in known_keys."""
    lines = []
    for key, value in item.model_dump(exclude_none=True).items():
        if key in known_keys:
            continue
        formatted = _format_value(value)
        if formatted:
            lines.append(f"- **{key}:** {formatted}")
    return lines


def format_fields(account: AccountFields) -> str:
    if not account.fields:
        return "No custom fields found."

    lines = []

    for entity, entity_fields in account.fields.items():
        entity_groups = account.groups.get(entity, {})
        lines.append(f"## {entity}")

        by_group: dict[str, list[tuple[str, object]]] = {}
        for key, field in entity_fields.items():
            group_key = field.group
            by_group.setdefault(group_key, []).append((key, field))

        for group_key, group_fields in by_group.items():
            group_name = entity_groups.get(group_key, group_key)
            lines.append(f"\n### {group_name}")

            for key, field in group_fields:
                line = f"- **{field.label or key}** (`{key}`) — {field.type}"

                if field.options:
                    option_labels = [o.label for o in field.options if o.label]
                    if option_labels:
                        line += f" — options: {', '.join(option_labels)}"

                lines.append(line)

        lines.append("")

    return "\n".join(lines)


def format_tags(tags: list[Tag], total: int | None = None, offset: int = 0) -> str:
    if not tags:
        return "No tags found."

    lines = []

    if total is not None:
        lines.append(_pagination_header("tags", len(tags), total, offset))

    known_keys = {"id", "name", "color"}
    for tag in tags:
        if tag.name:
            lines.append(f"- **{tag.name}** (color: `{tag.color}`, id: `{tag.id}`)")
            lines.extend(_format_extra_fields(tag, known_keys))

    return "\n".join(lines)


def format_deals(deals: list[Deal], total: int | None = None, offset: int = 0) -> str:
    if not deals:
        return "No deals found."

    lines = []

    if total is not None:
        lines.append(_pagination_header("deals", len(deals), total, offset))

    known_keys = {
        "id", "status", "stage", "value", "contact", "user",
        "created_at", "updated_at", "won_at", "lost_at", "fields",
    }

    for deal in deals:
        contact = deal.contact
        user = deal.user
        contact_name = (contact.name or "No name") if contact else "No name"

        lines.append(f"### {contact_name}")
        lines.append(f"- **id:** {deal.id}")
        lines.append(f"- **status:** {deal.status}")
        lines.append(f"- **stage:** {deal.stage}")
        lines.append(f"- **value:** {deal.value}")

        # Contact info
        if contact:
            if contact.phone:
                lines.append(f"- **phone:** {contact.ddi or ''}{contact.phone}")
            if contact.email:
                lines.append(f"- **email:** {contact.email}")
            if contact.instagram:
                ig = contact.instagram.get("username", contact.instagram) if isinstance(contact.instagram, dict) else contact.instagram
                lines.append(f"- **instagram:** {ig}")

        # User (responsible)
        if user and user.full_name:
            lines.append(f"- **responsible:** {user.full_name} ({user.email})")

        # Dates
        for date_key in ("created_at", "updated_at", "won_at", "lost_at"):
            date_val = getattr(deal, date_key)
            if date_val:
                lines.append(f"- **{date_key}:** {date_val}")

        # Custom fields
        if deal.fields:
            lines.append("- **fields:**")
            for key, value in deal.fields.items():
                formatted = _format_value(value)
                if formatted:
                    lines.append(f"  - {key}: {formatted}")

        # Extra fields not explicitly handled
        lines.extend(_format_extra_fields(deal, known_keys))

        lines.append("")

    return "\n".join(lines)


def format_groups(
    groups: list[Group], total: int | None = None, offset: int = 0
) -> str:
    if not groups:
        return "No groups found."

    lines = []

    if total is not None:
        lines.append(_pagination_header("groups", len(groups), total, offset))

    known_keys = {"id", "name", "archived_at"}
    for group in groups:
        line = f"- **{group.name}** (id: `{group.id}`)"
        if group.archived_at:
            line += f" — archived at {group.archived_at}"
        lines.append(line)
        lines.extend(_format_extra_fields(group, known_keys))

    return "\n".join(lines)


def format_lost_status(
    items: list[LostStatus], total: int | None = None, offset: int = 0
) -> str:
    if not items:
        return "No lost status found."

    lines = []

    if total is not None:
        lines.append(_pagination_header("lost status", len(items), total, offset))

    known_keys = {"id", "name"}
    for item in items:
        lines.append(f"- **{item.name}** (id: `{item.id}`)")
        lines.extend(_format_extra_fields(item, known_keys))

    return "\n".join(lines)


def format_origins(
    origins: list[Origin], total: int | None = None, offset: int = 0
) -> str:
    if not origins:
        return "No origins found."

    lines = []

    if total is not None:
        lines.append(_pagination_header("origins", len(origins), total, offset))

    known_keys = {"id", "name", "archived_at", "group", "stages"}
    for origin in origins:
        lines.append(f"### {origin.name}")
        lines.append(f"- **id:** {origin.id}")

        if origin.group and origin.group.name:
            lines.append(f"- **group:** {origin.group.name}")

        if origin.archived_at:
            lines.append(f"- **archived at:** {origin.archived_at}")

        if origin.stages:
            sorted_stages = sorted(origin.stages, key=lambda s: s.order)
            lines.append("- **stages:**")
            for s in sorted_stages:
                lines.append(f"  - {s.order}. {s.label} (id: {s.id})")

        lines.extend(_format_extra_fields(origin, known_keys))

        lines.append("")

    return "\n".join(lines)


def format_users(
    users: list[User], total: int | None = None, offset: int = 0
) -> str:
    if not users:
        return "No users found."

    lines = []

    if total is not None:
        lines.append(_pagination_header("users", len(users), total, offset))

    known_keys = {"id", "first_name", "last_name", "email"}
    for user in users:
        lines.append(
            f"- **{user.first_name} {user.last_name}** ({user.email}) — id: `{user.id}`"
        )
        lines.extend(_format_extra_fields(user, known_keys))

    return "\n".join(lines)


def format_contacts(
    contacts: list[Contact], total: int | None = None, offset: int = 0
) -> str:
    if not contacts:
        return "No contacts found."

    lines = []

    if total is not None:
        lines.append(_pagination_header("contacts", len(contacts), total, offset))

    for item in contacts:
        lines.append(f"### {item.name}")

        for key, value in item.model_dump(exclude_none=True).items():
            if key == "name":
                continue
            formatted = _format_value(value)
            if not formatted:
                continue
            lines.append(f"- **{key}:** {formatted}")

        lines.append("")

    return "\n".join(lines)


def format_organization(org: Organization) -> str:
    lines = [f"### {org.name or 'No name'}", f"- **id:** {org.id}"]

    if org.custom_fields:
        lines.append("- **custom fields:**")
        for key, value in org.custom_fields.items():
            formatted = _format_value(value)
            if formatted:
                lines.append(f"  - {key}: {formatted}")

    known_keys = {"id", "name", "custom_fields"}
    lines.extend(_format_extra_fields(org, known_keys))

    return "\n".join(lines)
