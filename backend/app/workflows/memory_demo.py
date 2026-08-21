import asyncio

from agents import Runner, SQLiteSession

from app.workflows.openai_ticket_agent import ticket_agent


async def main() -> None:
    session = SQLiteSession(
        "merchant_support_demo",
        "app/data/agent_memory.db",
    )

    # Clear earlier demo history so this test starts predictably.
    await session.clear_session()

    print("\nTURN 1: Investigating TKT0001\n")

    first_result = await Runner.run(
        ticket_agent,
        "Investigate ticket TKT0001 using the available tools.",
        session=session,
    )

    print(first_result.final_output.model_dump_json(indent=2))

    print("\nTURN 2: Referring to the same ticket without its ID\n")

    second_result = await Runner.run(
        ticket_agent,
        (
            "Using the ticket we just investigated, provide a shorter "
            "merchant response. I am deliberately not repeating the ticket ID."
        ),
        session=session,
    )

    print(second_result.final_output.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())