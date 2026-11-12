from drafter import *
from dataclasses import dataclass


# Stores information about one fish
@dataclass
class Fish_Caught:
    size: float
    weight: float
    species: str


# Stores all information for the website
@dataclass
class State:
    size: float
    weight: float
    species: str
    history: list[Fish_Caught]


@route
def index(state: State) -> Page:
    """Display the homepage and website navigation."""
    return Page(state, [
        Header("Pennsylvania Fishing Logbook"),
        Text("Welcome to your personal fishing logbook!"),
        Text("Record your catches and view your fishing statistics."),
        Header("Navigation"),
        Button("Log a Fish", "log_fish"),
        Button("Fishing Statistics", "fish_stats"),
        Button("Keep or Release Checker", "keep_or_release"),
        Button("Catch History", "catch_history"),
        Button("Average Catch", "average_catch"),
    ])



@route
def log_fish(state: State) -> Page:
    """Display the form for logging a fish."""
    return Page(state, [
        Header("Log a Fish"),
        Text("Enter the information about your catch."),
        
        Text("Fish Species:"),
        TextBox("species"),
        
        Text("Length (inches):"),
        TextBox("size", 0.0, "number"),
        
        Text("Weight (pounds):"),
        TextBox("weight", 0.0, "number"),
        
        Button("Submit Fish", "save_fish"),
        Button("Home", "index")
    ])


@route
def save_fish(state: State, species: str,
              size: float, weight: float) -> Page:
    """Validate and save a fish into the catch history."""

    # Make sure the user entered a species
    if species.strip() == "":
        return Page(state, [
            Header("Missing Information"),
            Text("Please enter a fish species."),
            Button("Go Back", "log_fish")
        ])

    # Make sure the measurements are positive
    if size <= 0 or weight <= 0:
        return Page(state, [
            Header("Invalid Measurements"),
            Text("Length and weight must be greater than zero."),
            Button("Try Again", "log_fish")
        ])

    # Create a new fish
    new_fish = Fish_Caught(size, weight, species.strip())

    # Update the website state
    state.size = size
    state.weight = weight
    state.species = species.strip()

    # Add the fish to the history
    state.history.append(new_fish)

    return Page(state, [
        Header("Fish Successfully Logged!"),
        Text("Your fish has been added to your catch history."),
        Text("Species: " + state.species),
        Text("Length: " + str(state.size) + " inches"),
        Text("Weight: " + str(state.weight) + " pounds"),
        Button("Log Another Fish", "log_fish"),
        Button("View Catch History", "catch_history"),
        Button("Home", "index")
    ])


@route
def fish_stats(state: State) -> Page:
    """Display statistics about the fish caught."""
    content = [
        Header("Fishing Statistics"),
        Text("Your personal fishing statistics:")
    ]

    if len(state.history) == 0:
        content.append(Text("You haven't logged any fish yet."))
    else:
        longest_fish = state.history[0]
        heaviest_fish = state.history[0]
        species_counts: dict[str, int] = {}

        for fish in state.history:
            if fish.size > longest_fish.size:
                longest_fish = fish

            if fish.weight > heaviest_fish.weight:
                heaviest_fish = fish

            if fish.species in species_counts:
                species_counts[fish.species] += 1
            else:
                species_counts[fish.species] = 1

        most_caught = max(species_counts, key=lambda species: species_counts[species])

        content.append(Text(
            "Total Fish Caught: " + str(len(state.history))
        ))
        content.append(Text(
            "Longest Fish: " + longest_fish.species
            + " (" + str(longest_fish.size) + " inches)"
        ))
        content.append(Text(
            "Heaviest Fish: " + heaviest_fish.species
            + " (" + str(heaviest_fish.weight) + " pounds)"
        ))
        content.append(Text(
            "Most Caught Species: " + most_caught
            + " (" + str(species_counts[most_caught]) + " caught)"
        ))

    content.append(Button("View Catch History", "catch_history"))
    content.append(Button("Log Another Fish", "log_fish"))
    content.append(Button("Home", "index"))

    return Page(state, content)



@route
def keep_or_release(state: State) -> Page:
    """Display the Pennsylvania keep or release checker."""
    return Page(state, [
        Header("Pennsylvania Keep or Release Checker"),
        Text("Enter information about the fish you caught."),

        "Fish Species:",
        TextBox("species"),

        "Fish Length (inches):",
        TextBox("size", 0.0, "number"),

        "Date Caught (YYYY-MM-DD):",
        TextBox("catch_date"),

        "Waterway (lake, river, or stream):",
        TextBox("waterway"),

        Button("Check Regulations", "check_regulations"),
        Button("Home", "index")
    ])


@route
def check_regulations(state: State, species: str,
                      size: float, catch_date: str,
                      waterway: str) -> Page:
    """Check basic Pennsylvania fishing season restrictions."""

    result = ""

    # Check for missing information
    if species.strip() == "" or waterway.strip() == "":
        result = "Please enter the species and waterway."

    elif size <= 0:
        result = "Please enter a valid fish length."

    # Check the date format
    elif (len(catch_date) != 10 or
          catch_date[4] != "-" or
          catch_date[7] != "-"):
        result = "Enter the date as YYYY-MM-DD."

    else:
        try:
            year = int(catch_date[0:4])
            month = int(catch_date[5:7])
            day = int(catch_date[8:10])

            # Check that the date is valid
            if month < 1 or month > 12:
                result = "Invalid month."

            elif day < 1 or day > 31:
                result = "Invalid day."

            elif year != 2026:
                result = "This checker currently covers 2026."

            else:
                fish = species.strip().lower()

                # Check Pennsylvania bass regulations
                if fish in ["bass", "largemouth bass",
                            "smallmouth bass", "spotted bass"]:

                    # 2026 statewide bass no-harvest season
                    if ((month == 4 and day >= 11) or
                        (month == 5) or
                        (month == 6 and day < 13)):
                        result = (
                            "RELEASE THE FISH. Pennsylvania's "
                            "statewide bass no-harvest season "
                            "is in effect on this date."
                        )

                    else:
                        result = (
                            "The date is outside the statewide "
                            "bass no-harvest season. Check the "
                            "minimum length, daily limit, and "
                            "special waterway regulations before "
                            "keeping the fish."
                        )

                # Check trout regulations
                elif fish in ["trout", "rainbow trout",
                              "brown trout", "brook trout"]:

                    result = (
                        "Trout regulations depend on the type "
                        "of waterway and its classification. "
                        "Check the current PFBC trout regulations "
                        "before deciding whether to keep this fish."
                    )

                else:
                    result = (
                        "This species is not included in the "
                        "current checker. Consult Pennsylvania's "
                        "official fishing regulations."
                    )

        except ValueError:
            result = "Please enter a valid date."

    return Page(state, [
        Header("Regulation Results"),
        Text(result),
        Text("Species: " + species),
        Text("Length: " + str(size) + " inches"),
        Text("Date: " + catch_date),
        Text("Waterway: " + waterway),
        Button("Check Another Fish", "keep_or_release"),
        Button("Home", "index")
    ])


@route
def catch_history(state: State) -> Page:
    """Display all fish saved in the catch history."""

    content = [
        Header("Catch History"),
        Text("Here are all the fish you have logged."),
        Text("Total Fish Caught: " + str(len(state.history)))
    ]

    # Check if any fish have been logged
    if len(state.history) == 0:
        content.append(Text("You haven't logged any fish yet."))

    # Display each fish in the history
    for fish in state.history:
        content.append(Header(fish.species))
        content.append(Text(
            "Length: " + str(fish.size) + " inches"
        ))
        content.append(Text(
            "Weight: " + str(fish.weight) + " pounds"
        ))

    content.append(Button("Log Another Fish", "log_fish"))
    content.append(Button("Home", "index"))

    return Page(state, content)


@route
def average_catch(state: State) -> Page:
    """Display average fish length and weight."""

    total_size = 0.0
    total_weight = 0.0
    total_fish = len(state.history)

    # Calculate the total length and weight
    for fish in state.history:
        total_size += fish.size
        total_weight += fish.weight

    content = [
        Header("Average Catch"),
        Text("Your fishing statistics:")
    ]

    # Check whether any fish have been logged
    if total_fish == 0:
        content.append(Text("No fish have been logged yet."))
    else:
        average_size = total_size / total_fish
        average_weight = total_weight / total_fish

        content.append(Text(
            "Total Fish Caught: " + str(total_fish)
        ))
        content.append(Text(
            "Average Length: " + str(round(average_size, 2))
            + " inches"
        ))
        content.append(Text(
            "Average Weight: " + str(round(average_weight, 2))
            + " pounds"
        ))

    content.append(Button("View Catch History", "catch_history"))
    content.append(Button("Log Another Fish", "log_fish"))
    content.append(Button("Home", "index"))

    return Page(state, content)



@route
def fish_information(state: State) -> Page:
    """Display information about different fish species."""
    return Page(state, [
        Header("Fish Information"),
        Text("Information about Pennsylvania fish will appear here."),
        Button("Home", "index")
    ])


set_website_title("Pennsylvania Fishing Logbook")

set_site_information(
    "Your Name",
    "A fishing logbook and Pennsylvania fishing regulations checker.",
    "Pennsylvania Fish and Boat Commission",
    "See the planning document in the GitHub repository.",
    ["https://www.pa.gov/agencies/fishandboat"]
)


page = log_fish(State(0.0, 0.0, "", []))

assert_equal(page.state, State(0.0, 0.0, "", []))

# Test that a fish is saved correctly
assert_state(
    save_fish(
        State(0.0, 0.0, "", []),
        "Bass",
        12.0,
        2.5
    ),
    State(
        12.0,
        2.5,
        "Bass",
        [Fish_Caught(12.0, 2.5, "Bass")]
    )
)


# Test average calculations
test_state = State(
    0.0, 0.0, "", [
        Fish_Caught(12.0, 2.5, "Bass"),
        Fish_Caught(16.0, 1.8, "Trout"),
        Fish_Caught(20.0, 5.2, "Catfish")
    ]
)

average_page = average_catch(test_state)

assert_equal(average_page.state, test_state)

start_server(State(0.0, 0.0, "", []))

