#!/usr/bin/env python
import asyncio
from typing import List, Optional
import datetime  # Add this import for timestamp

from crewai.flow.flow import Flow, listen, start, router
from pydantic import BaseModel

from self_evaluation_loop_flow.crews.book_chapter_crew.book_chapter_crew import (
    WriteBookChapterCrew,
)
from self_evaluation_loop_flow.Types import Chapter, ChapterOutline
from self_evaluation_loop_flow.crews.book_outline_review_crew.book_outline_review_crew import (
    BookOutlineReviewCrew,
)

from .crews.book_outline_crew.book_outline_crew import BookOutlineCrew


class BookState(BaseModel):
    title: str = "Dreamwalkers of the Dystopian Future"
    book: List[Chapter] = []
    book_outline: List[ChapterOutline] = []
    topic: str = (
        "A dystopian future where the government controls all forms of media and information, and the people are kept in a state of constant surveillance and control."
    )
    plot: str = (
        "In the aftermath of a devastating global catastrophe, humanity's survival depends on "
        "genetically engineered superhumans like Eve, who has been tasked with repopulating Earth. "
        "As Eve begins her mission, she discovers an unexpected evolution in human biology: "
        "telepathy has emerged among survivors.\n\n"
        "The government, led by the ruthless Puppet Master (Lucian Fez), has outlawed telepathy, "
        "fearing its potential to destabilize their control. In this oppressive society where "
        "privacy is paramount, Eve encounters Luna, the charismatic leader of the Dreamwalkers—an "
        "underground group of psychics who can navigate and manipulate dreams to bypass the "
        "telepathically-shielded society.\n\n"
        "As Eve delves deeper into the world of the Dreamwalkers, she finds herself caught between "
        "her duty to repopulate Earth and her growing loyalty to these persecuted psychics. "
        "Meanwhile, she discovers shocking truths about her own origins: she was created using DNA "
        "from Lucian Fez's late wife, Iris, making her genetically related to Lucian's daughter, "
        "Lady Seraphina Fez—a powerful telepath who secretly hides her abilities from her father.\n\n"
        "Eve and Luna must ultimately join forces to expose the Puppet Master's nefarious plans "
        "and fight for a world where telepathy is accepted rather than persecuted. Their journey "
        "becomes a battle for the very definition of humanity in this post-apocalyptic world, "
        "challenging notions of identity, connection, and resilience in the face of overwhelming "
        "opposition."
    )
    characters: str = ("""
    Eve (22):
    - A genetically engineered superhuman with enhanced strength, speed, and durability
    - Created using DNA from Lucian's late wife Iris, making her related to Seraphina Fez
    - Tall with an athletic build, golden skin, wild curly brown hair, and piercing emerald eyes
    - Wears a sleek black and silver jumpsuit with integrated armor and circuitry patterns
    - Compassionate and determined, driven by her duty to humanity
    - Struggles with understanding telepathy and finding her place in the new world
    - Primary motivation: To escape government control and forge her own identity

    Luna (Mid-30s):
    - Enigmatic leader of the Dreamwalkers and former government operative
    - Defected upon discovering the truth about telepathy and the regime's plans
    - Intelligent, resourceful, and fiercely loyal to her fellow Dreamwalkers
    - Determined to protect her people and expose government corruption
    - Her mysterious past adds complexity to the narrative

    Lucian Fez (Late 40s) - The Puppet Master:
    - Ruthless government official leading the crusade against telepathy
    - Cold, calculating and consumed by paranoia regarding psychic abilities
    - Born into privilege as son of Marcellus Fez, a high-ranking official
    - Childhood trauma: His sister Elara was a telepath who died under their father's cruel "treatment"
    - Adult trauma: His beloved wife Iris (a telepath) died after being experimented on
    - Driven by fear, paranoia, and unresolved guilt about his sister and wife
    - Views all telepaths as threats that must be eliminated

    Lady Seraphina Fez (Early 20s):
    - Daughter of Lucian Fez and a brilliant telepath with exceptional powers
    - Keeps her abilities secret from her father out of fear
    - Raised in privilege but empathetic and yearning for freedom
    - Deeply conflicted between loyalty to her father and her telepathic nature
    - Genetically related to Eve through her mother Iris's DNA

    Secondary Characters:

    Leonardo Moreno (Late 30s):
    - Senior official in the Ministry of Psychic Affairs
    - Staunch supporter of Lucian's anti-telepathy policies
    - Secret admirer of Lady Seraphina
    - Begins questioning the morality of the government's actions
    - Caught between his loyalty to Lucian and his feelings for Seraphina

    The Dreamwalkers (The Dream Legion):

    Alaric (Late 20s):
    - Skilled in entering and controlling dreams with precision
    - Calm, collected, and possesses deep knowledge of the dreamscape
    - Expert fighter from years of secret training
    - Struggles with trust issues and develops complicated feelings for Eve
    - Intensely loyal to the Dreamwalkers

    Zara (Early 20s):
    - Mind-reading Dreamwalker with strong empathic abilities
    - Can sense others' thoughts and emotions
    - Expert in psychological warfare and intelligence gathering
    - Fiery, passionate, and deeply compassionate
    - Becomes Eve's emotional confidante and guide

    Kai (Mid-20s):
    - Charismatic Dreamwalker who projects himself into others' dreams
    - Strategic thinker crucial in protecting fellow Dreamwalkers
    - Charming, confident, and intensely curious about the dream world
    - Provides comic relief and contrasts with Alaric's serious nature
    - Driven by wonder and desire for adventure
    """
    )
    feedback: Optional[str] = None
    valid: bool = False
    retry_count: int = 0


class BookFlow(Flow[BookState]):
    initial_state = BookState

    @start("retry")
    def generate_book_outline(self):
        print("Kickoff the Book Outline Crew")
        output = (
            BookOutlineCrew()
            .crew()
            .kickoff(inputs={"topic": self.state.topic, "plot": self.state.plot, "characters": self.state.characters, "feedback": self.state.feedback})
        )
        chapters = output["chapters"]
        print("Chapters:", chapters)

        self.state.book_outline = chapters
        return chapters
    
    @router(generate_book_outline)
    def evaluate_book_outline(self):
        if self.state.retry_count > 3:
            return "max_retry_exceeded"

        result = BookOutlineReviewCrew().crew().kickoff(inputs={"book_outline": self.state.book_outline})
        self.state.valid = result["valid"]
        self.state.feedback = result["feedback"]

        print("valid", self.state.valid)
        print("feedback", self.state.feedback)
        self.state.retry_count += 1

        if self.state.valid:
            return "completed"

        print("RETRY")
        return "retry" 
    
    @listen("completed")
    def save_result(self):
        print("Book outline is valid")
        print("Book outline:", self.state.book_outline)

        # Save the valid book outline to a file
        with open("book_outline.txt", "w") as file:
            # Convert the list of ChapterOutline objects to a string representation
            outline_text = ""
            for i, chapter in enumerate(self.state.book_outline, 1):
                outline_text += f"Chapter {i}: {chapter.title}\n"
                outline_text += f"Description: {chapter.description}\n\n"
            file.write(outline_text)

    @listen("max_retry_exceeded")
    def max_retry_exceeded_exit(self):
        print("Max retry count exceeded")
        print("Book outline:", self.state.book_outline)
        print("Feedback:", self.state.feedback)

    @listen("completed")
    async def write_chapters(self):
        print("Writing Book Chapters")
        tasks = []

        async def write_single_chapter(chapter_outline):
            output = (
                WriteBookChapterCrew()
                .crew()
                .kickoff(
                    inputs={
                        "plot": self.state.plot,
                        "topic": self.state.topic,
                        "chapter_title": chapter_outline.title,
                        "chapter_description": chapter_outline.description,
                        "book_outline": [
                            chapter_outline.model_dump_json()
                            for chapter_outline in self.state.book_outline
                        ],
                    }
                )
            )
            title = output["title"]
            content = output["content"]
            chapter = Chapter(title=title, content=content)
            return chapter

        for chapter_outline in self.state.book_outline:
            print(f"Writing Chapter: {chapter_outline.title}")
            print(f"Description: {chapter_outline.description}")
            # Schedule each chapter writing task
            task = asyncio.create_task(write_single_chapter(chapter_outline))
            tasks.append(task)

        # Await all chapter writing tasks concurrently
        chapters = await asyncio.gather(*tasks)
        print("Newly generated chapters:", chapters)
        self.state.book.extend(chapters)

        print("Book Chapters", self.state.book)

    @listen(write_chapters)
    async def join_and_save_chapter(self):
        print("Joining and Saving Book Chapters")
        # Combine all chapters into a single markdown string
        book_content = ""

        for chapter in self.state.book:
            # Add the chapter title as an H1 heading
            book_content += f"# {chapter.title}\n\n"
            # Add the chapter content
            book_content += f"{chapter.content}\n\n"

        # The title of the book from self.state.title
        book_title = self.state.title
        
        # Get current timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create the filename by replacing spaces with underscores, adding timestamp and .md extension
        filename = f"./{book_title.replace(' ', '_')}_{timestamp}.md"

        # Save the combined content into the file
        with open(filename, "w", encoding="utf-8") as file:
            file.write(book_content)

        print(f"Book saved as {filename}")
        return book_content


def kickoff():
    poem_flow = BookFlow()
    poem_flow.kickoff()


def plot():
    poem_flow = BookFlow()
    poem_flow.plot()


def display_book():
    """
    Display the book outline and chapters in a readable format.
    This function loads the generated book file and prints its structure.
    """
    # Create a new BookFlow instance
    book_flow = BookFlow()
    
    # Generate the book outline
    print("\n===== BOOK OUTLINE =====")
    print(f"Title: {book_flow.state.title}")
    print(f"Topic: {book_flow.state.topic}")
    print("\nChapters:")
    
    # Check if the book outline has been generated
    if not book_flow.state.book_outline:
        print("Book outline has not been generated yet. Run kickoff() first.")
        return
    
    # Display the book outline
    for i, chapter_outline in enumerate(book_flow.state.book_outline, 1):
        print(f"\nChapter {i}: {chapter_outline.title}")
        print(f"Description: {chapter_outline.description}")
    
    # Check if chapters have been written
    if not book_flow.state.book:
        print("\nChapters have not been written yet. Run kickoff() first.")
        return
    
    # Display chapter summaries
    print("\n===== CHAPTER SUMMARIES =====")
    for i, chapter in enumerate(book_flow.state.book, 1):
        print(f"\nChapter {i}: {chapter.title}")
        # Display first 200 characters of content as a preview
        preview = chapter.content[:200] + "..." if len(chapter.content) > 200 else chapter.content
        print(f"Preview: {preview}")
    
    # Get current timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Display file location
    book_title = book_flow.state.title
    filename = f"./{book_title.replace(' ', '_')}_{timestamp}.md"
    print(f"\nFull book will be saved as: {filename}")


def read_book(filename=None):
    """
    Read and display the generated book from the markdown file.
    
    Args:
        filename (str, optional): The path to the markdown file. 
                                 If None, tries to find the most recent book file.
    """
    # If filename is not provided, try to find the most recent book file
    if filename is None:
        import glob
        import os
        
        book_flow = BookFlow()
        book_title = book_flow.state.title
        base_filename = f"./{book_title.replace(' ', '_')}_"
        
        # Find all files matching the pattern
        matching_files = glob.glob(f"{base_filename}*.md")
        
        if matching_files:
            # Sort files by modification time (most recent first)
            matching_files.sort(key=os.path.getmtime, reverse=True)
            filename = matching_files[0]
            print(f"Reading most recent book file: {filename}")
        else:
            # If no matching files found, create a filename with current timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{base_filename}{timestamp}.md"
            print(f"No existing book files found. Will look for: {filename}")
    
    try:
        # Read the markdown file
        with open(filename, "r", encoding="utf-8") as file:
            content = file.read()
        
        # Print the book content
        print(f"\n===== BOOK CONTENT: {filename} =====\n")
        print(content)
        
        # Print statistics
        chapter_count = content.count("# ")
        word_count = len(content.split())
        print(f"\n===== BOOK STATISTICS =====")
        print(f"Chapters: {chapter_count}")
        print(f"Word count: {word_count}")
        print(f"Character count: {len(content)}")
        
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        print("Make sure you've run kickoff() to generate the book first.")
    except Exception as e:
        print(f"Error reading the book file: {str(e)}")


def list_books():
    """
    List all generated book files with their timestamps and sizes.
    """
    import glob
    import os
    from datetime import datetime
    
    book_flow = BookFlow()
    book_title = book_flow.state.title
    base_filename = f"./{book_title.replace(' ', '_')}_"
    
    # Find all files matching the pattern
    matching_files = glob.glob(f"{base_filename}*.md")
    
    if not matching_files:
        print(f"No book files found matching the pattern: {base_filename}*.md")
        return
    
    # Sort files by modification time (most recent first)
    matching_files.sort(key=os.path.getmtime, reverse=True)
    
    print(f"\n===== GENERATED BOOK FILES =====")
    print(f"{'Filename':<50} {'Size (KB)':<10} {'Last Modified':<20}")
    print("-" * 80)
    
    for file_path in matching_files:
        # Get file stats
        stats = os.stat(file_path)
        size_kb = stats.st_size / 1024
        mod_time = datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        
        # Print file info
        print(f"{os.path.basename(file_path):<50} {size_kb:<10.2f} {mod_time:<20}")
    
    print(f"\nTotal files: {len(matching_files)}")


if __name__ == "__main__":
    import sys
    
    # Check if command line arguments are provided
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "kickoff":
            kickoff()
        elif command == "plot":
            plot()
        elif command == "display":
            display_book()
        elif command == "read":
            # Check if a filename is provided
            if len(sys.argv) > 2:
                read_book(sys.argv[2])
            else:
                read_book()
        elif command == "list":
            list_books()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: kickoff, plot, display, read, list")
    else:
        # Default behavior: run kickoff
        print("Running kickoff() by default. Use command line arguments for other functions:")
        print("  python -m self_evaluation_loop_flow.main kickoff  - Generate the book")
        print("  python -m self_evaluation_loop_flow.main plot     - Generate a flow diagram")
        print("  python -m self_evaluation_loop_flow.main display  - Display book outline and chapter summaries")
        print("  python -m self_evaluation_loop_flow.main read     - Read the generated book")
        print("  python -m self_evaluation_loop_flow.main list     - List all generated book files")
        kickoff()