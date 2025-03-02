#!/usr/bin/env python
import asyncio
from typing import List
import datetime  # Add this import for timestamp

from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel

from self_evaluation_loop_flow.crews.book_chapter_crew.book_chapter_crew import (
    WriteBookChapterCrew,
)
from self_evaluation_loop_flow.Types import Chapter, ChapterOutline

from .crews.book_outline_crew.book_outline_crew import BookOutlineCrew


class BookState(BaseModel):
    title: str = "The Current State of AI in September 2024"
    book: List[Chapter] = []
    book_outline: List[ChapterOutline] = []
    topic: str = (
        "Exploring the latest trends in AI across different industries as of September 2024"
    )
    goal: str = """
        The goal of this book is to provide a comprehensive overview of the current state of artificial intelligence in September 2024.
        It will delve into the latest trends impacting various industries, analyze significant advancements,
        and discuss potential future developments. The book aims to inform readers about cutting-edge AI technologies
        and prepare them for upcoming innovations in the field.
    """


class BookFlow(Flow[BookState]):
    initial_state = BookState

    @start()
    def generate_book_outline(self):
        print("Kickoff the Book Outline Crew")
        output = (
            BookOutlineCrew()
            .crew()
            .kickoff(inputs={"topic": self.state.topic, "goal": self.state.goal})
        )

        chapters = output["chapters"]
        print("Chapters:", chapters)

        self.state.book_outline = chapters
        return chapters

    @listen(generate_book_outline)
    async def write_chapters(self):
        print("Writing Book Chapters")
        tasks = []

        async def write_single_chapter(chapter_outline):
            output = (
                WriteBookChapterCrew()
                .crew()
                .kickoff(
                    inputs={
                        "goal": self.state.goal,
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