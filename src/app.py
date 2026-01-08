"""
Gradio web interface for the LM Studio QA Agent.

Provides three main tabs:
- Test Generator: Generate Playwright tests from URL and description
- Vision Agent: Generate tests using vision-capable LLMs
- Self-Healer: Automatically repair broken test files
"""
import os
import sys

# Add the project root to sys.path to support 'src.' imports when run as a script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import gradio as gr

from src.agents.generator import generate_test_script, run_generated_test
from src.agents.healer import attempt_healing
from src.agents.vision import analyze_visual_ui
from src.utils.validation import validate_and_sanitize_url, validate_description, ValidationError

# Custom CSS matching Gradio website style
css = """
.tall-textbox textarea { min-height: 300px !important; }
.tall-code .code-container { min-height: 400px !important; }
/* Match Gradio website typography and spacing */
h1 { 
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-weight: 600;
    color: #1f2937;
    letter-spacing: -0.025em;
}
/* Clean component styling */
.gradio-container {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}
"""

# Use default theme for standard Gradio appearance
with gr.Blocks(title="LM Studio QA Agent") as demo:
    gr.Markdown("# LM Studio QA Agent")
    gr.Markdown("Generate, test, and maintain Playwright test automation scripts.")

    with gr.Tabs():
        # Tab 1: Test Generator
        with gr.Tab("Test Generator"):
            with gr.Row():
                with gr.Column(scale=1):
                    url_in = gr.Textbox(
                        label="Target URL",
                        placeholder="https://example.com",
                        value="https://the-internet.herokuapp.com/login"
                    )
                    story_in = gr.Textbox(
                        label="Test Scenario",
                        placeholder="Describe the test scenario...",
                        value="Login with tomsmith and SuperSecretPassword!. Verify success message.",
                        lines=3
                    )
                    gen_btn = gr.Button("Generate Test", variant="primary")

                with gr.Column(scale=1):
                    code_out = gr.Code(
                        label="Generated Code",
                        language="typescript",
                        lines=20,
                        elem_classes=["tall-code"]
                    )
                    with gr.Row():
                        run_btn = gr.Button("Run Test", variant="secondary")
                    result_out = gr.Textbox(
                        label="Execution Result",
                        interactive=False,
                        lines=12,
                        elem_classes=["tall-textbox"]
                    )


            def safe_generate_test(url, story):
                """Generate test script with input validation and error handling."""
                try:
                    validated_url = validate_and_sanitize_url(url)
                    validated_story = validate_description(story)
                    return generate_test_script(validated_url, validated_story)
                except ValidationError as e:
                    return f"Validation Error: {str(e)}"
                except Exception as e:
                    return f"Error: {str(e)}"


            def safe_run_test(url, code, story):
                """Run generated test with input validation and error handling."""
                try:
                    validated_url = validate_and_sanitize_url(url)
                    validated_story = validate_description(
                        story) if story else "test"
                    return run_generated_test(validated_url, code, validated_story)
                except ValidationError as e:
                    return f"Validation Error: {str(e)}"
                except Exception as e:
                    return f"Error: {str(e)}"


            gen_btn.click(fn=safe_generate_test, inputs=[
                url_in, story_in], outputs=code_out)
            run_btn.click(fn=safe_run_test, inputs=[
                url_in, code_out, story_in], outputs=result_out)

        # Tab 2: Vision Agent
        with gr.Tab("Vision Agent"):
            gr.Markdown("Generate tests using vision-capable LLMs to analyze UI screenshots.")
            with gr.Row():
                with gr.Column(scale=1):
                    v_url_in = gr.Textbox(
                        label="Target URL",
                        placeholder="https://example.com",
                        value="https://www.saucedemo.com"
                    )
                    v_story_in = gr.Textbox(
                        label="Instruction",
                        placeholder="Describe the action to perform...",
                        value="Login with standard_user / secret_sauce",
                        lines=2
                    )
                    v_btn = gr.Button("Capture & Analyze", variant="primary")

                with gr.Column(scale=1):
                    v_code_out = gr.Code(
                        language="typescript",
                        label="Generated Code",
                        lines=20,
                        elem_classes=["tall-code"]
                    )
                    with gr.Row():
                        v_run_btn = gr.Button("Run Test", variant="secondary")
                    v_result_out = gr.Textbox(
                        label="Execution Result",
                        interactive=False,
                        lines=10,
                        elem_classes=["tall-textbox"]
                    )


            def safe_analyze_visual(url, instruction):
                """Analyze UI visually with input validation and error handling."""
                try:
                    validated_url = validate_and_sanitize_url(url)
                    validated_instruction = validate_description(instruction)
                    return analyze_visual_ui(validated_url, validated_instruction)
                except ValidationError as e:
                    return f"Validation Error: {str(e)}"
                except Exception as e:
                    return f"Error: {str(e)}"


            def safe_run_vision_test(url, code, instruction):
                """Run vision-generated test with input validation and error handling."""
                try:
                    validated_url = validate_and_sanitize_url(url)
                    validated_instruction = validate_description(
                        instruction) if instruction else "test"
                    return run_generated_test(validated_url, code, validated_instruction)
                except ValidationError as e:
                    return f"Validation Error: {str(e)}"
                except Exception as e:
                    return f"Error: {str(e)}"


            v_btn.click(fn=safe_analyze_visual, inputs=[
                v_url_in, v_story_in], outputs=v_code_out)
            v_run_btn.click(fn=safe_run_vision_test, inputs=[
                v_url_in, v_code_out, v_story_in], outputs=v_result_out)

        # Tab 3: Self-Healer
        with gr.Tab("Self-Healer"):
            gr.Markdown("Automatically repair broken Playwright tests by analyzing error logs.")
            with gr.Row():
                with gr.Column(scale=1):
                    h_file_in = gr.File(
                        label="Test File",
                        file_types=[".ts"],
                        file_count="single"
                    )
                    h_btn = gr.Button("Heal Test", variant="primary")

                with gr.Column(scale=1):
                    h_result_out = gr.Textbox(
                        label="Result",
                        interactive=False,
                        lines=15,
                        elem_classes=["tall-textbox"]
                    )


            def wrap_healer(file_obj):
                """Handle file upload from Gradio and attempt to heal the test file."""
                if file_obj is None:
                    return "Please upload a test file."
                try:
                    import shutil
                    from src.utils.validation import validate_file_path
                    # In Gradio 6.x, file_count="single" returns a string path directly
                    # Handle both string paths and file objects for compatibility
                    file_path = file_obj if isinstance(file_obj, str) else file_obj.name
                    # Ensure the file is in the project directory so Playwright can find the context
                    local_path = os.path.join(
                        "tests", "generated", os.path.basename(file_path))
                    # Validate the path before copying
                    validated_path = validate_file_path(local_path)
                    shutil.copy(file_path, validated_path)
                    return attempt_healing(validated_path)
                except ValidationError as e:
                    return f"Validation Error: {str(e)}"
                except Exception as e:
                    return f"Error: {str(e)}"


            h_btn.click(fn=wrap_healer, inputs=[
                h_file_in], outputs=h_result_out)

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Default(), css=css)
