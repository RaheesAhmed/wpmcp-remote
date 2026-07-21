"""Prompt templates that guide consistent, safe WordPress workflows."""

from __future__ import annotations

from fastmcp import FastMCP


def register_workflow_prompts(mcp: FastMCP) -> None:
    """Register reusable prompts discoverable by compatible MCP clients."""

    @mcp.prompt(
        name="wp_site_audit",
        title="Audit a WordPress site",
        description="Produce a health, security, and performance audit with prioritized actions.",
    )
    def wp_site_audit(site: str = "") -> str:
        target = site or "the default site"
        return (
            f"Audit {target}. Gather site info, site health, available updates, debug log "
            "summary, performance metrics, and a database table overview. Prioritize the top "
            "five actions by risk and impact. Do not perform writes."
        )

    @mcp.prompt(
        name="wp_content_sprint",
        title="Content sprint",
        description="Draft and publish a batch of posts with SEO and media.",
    )
    def wp_content_sprint(topic: str, count: int = 3) -> str:
        return (
            f"Plan and create {count} blog posts about '{topic}'. For each post: draft a "
            "compelling title and body, set SEO meta (meta description + focus keyword), "
            "assign sensible categories/tags, and leave them as drafts for review. Summarize "
            "what was created and what the user should approve before publishing."
        )

    @mcp.prompt(
        name="wp_hardening",
        title="Harden WordPress",
        description="Apply a safe hardening checklist without destructive changes.",
    )
    def wp_hardening(site: str = "") -> str:
        target = site or "the default site"
        return (
            f"Harden {target}. Verify core file checksums, scan file permissions, review "
            "failed logins, clear the cache, and clean up spam/trash. Report findings and "
            "recommend changes. Stop before any destructive or irreversible action and ask "
            "for explicit confirmation."
        )

    @mcp.prompt(
        name="wp_theme_build",
        title="Build a child theme",
        description="Scaffold a child theme and customize styles safely.",
    )
    def wp_theme_build(parent: str, name: str) -> str:
        return (
            f"Create a child theme '{name}' of '{parent}'. Read the parent's theme.json, "
            "create the child theme, add a starter style.css and custom.css, and apply one "
            "small visual tweak the user requests. Back up every file before writing."
        )

    @mcp.prompt(
        name="wp_woo_review",
        title="WooCommerce review",
        description="Summarize store performance and outstanding orders.",
    )
    def wp_woo_review(site: str = "") -> str:
        target = site or "the default site"
        return (
            f"Review the WooCommerce store on {target}. Pull a sales report, top sellers, "
            "open orders, low-stock products, and active coupons. Summarize performance and "
            "recommend the next three operational actions. Do not modify orders or stock."
        )
