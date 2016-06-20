"""This module maps instrucitons to SVG."""
import os
import xmltodict


REPLACE_IN_DEFAULT_SVG = "{instruction.type}"


class InstructionToSVG(object):
    """This class maps instructions to SVGs."""
    from knittingpattern.Loader import PathLoader as Loader

    def __init__(self):
        """Create a InstructionToSVG object."""
        self._instruction_type_to_file_content = {}

    @property
    def load(self):
        """Returns a loader object that allows loading SVG files from
        various sources such as files and folders.

        `load.path(path)` loads an SVG from a file named path
        `load.folder(path)` loads all SVG files for instructions in the folder
        recursively.
        If multiple files have the same name, the last occurrence is used."""
        return self.Loader(self._process_loaded_object)

    def _process_loaded_object(self, path):
        file_name = os.path.basename(path)
        name, ext = os.path.splitext(file_name)
        with open(path) as file:
            string = file.read()
            self._instruction_type_to_file_content[name] = string

    def instruction_to_svg(self, instruction):
        """Returns an SVG representing the instruction.

        The SVG file is determined by the type attribute of the instruction.
        An instruction of type "knit" is looked for in a file named "knit.svg".
        
        Every element inside a group labeled "color" of mode "layer" that has
        a "fill" style gets this fill replaced by the color of the instruction.
        Example of a recangle that gets filled like the instruction:

            <g inkscape:label="color" inkscape:groupmode="layer">
                <rect style="fill:#ff0000;fill-opacity:1;fill-rule:nonzero"
                      id="rectangle1" width="10" height="10" x="0" y="0" />
            </g>
        
        If nothing was loaded to display this instruction, a default image will
        be generated by `default_instruction_to_svg`.
        """
        instruction_type = instruction.type
        if instruction_type in self._instruction_type_to_file_content:
            svg_content = self._instruction_type_to_file_content[instruction_type]
            return self._set_fills_in_color_layer(svg_content, instruction.color)
        return self.default_instruction_to_svg(instruction)
        
    def _set_fills_in_color_layer(self, svg_string, color):
        """replaces fill colors in <g inkscape:label="color" 
        inkscape:groupmode="layer"> with color"""
        if color is None:
            return svg_string
        structure = xmltodict.parse(svg_string)
        layers = structure["svg"]["g"]
        if not isinstance(layers, list):
            layers = [layers]
        for layer in layers:
            print("layer:", layer)
            if not isinstance(layer, dict):
                continue
            if layer.get("@inkscape:label") == "color" and layer.get("@inkscape:groupmode") == "layer":
                for key, elements in layer.items():
                    if key.startswith("@") or key.startswith("#"):
                        continue
                    if not isinstance(elements, list):
                        elements = [elements]
                    for element in elements:
                        print("ELEMENT:", element)
                        style = element.get("@style", None)
                        if style:
                            print("style:", style)
                            style = style.split(";")
                            processed_style = []
                            for e in style:
                                if e.startswith("fill:"):
                                    e = "fill:" + color
                                processed_style.append(e)
                            style = ";".join(processed_style)
                            element["@style"] = style
        return xmltodict.unparse(structure)

    def has_svg_for_instruction(self, instruction):
        """Returns whether there is an image for the instruction.

        This can be used before `instruction_to_svg` as it determines whether
        - the default value is used (`False`)
        - or there is a dedicated svg representation (`True`).
        """
        instruction_type = instruction.type
        return instruction_type in self._instruction_type_to_file_content

    def default_instruction_to_svg(self, instruction):
        """As `instruction_to_svg()` but it only takes the "default.svg" file
        into account.

        In case no file is found for an instruction in `instruction_to_svg()`,
        this method is used to determine the default svg for it.

        The content is created by replacing the text "{instruction.type}" in
        the whole svg file named `default.svg`.

        If no file `default.svg` was loaded, an empty string is returned."""
        instruction_type = instruction.type
        default_type = "default"
        rep_str = "{instruction.type}"
        if default_type not in self._instruction_type_to_file_content:
            return ""
        default_svg = self._instruction_type_to_file_content[default_type]
        default_svg = default_svg.replace(rep_str, instruction_type)
        colored_svg = self._set_fills_in_color_layer(default_svg, instruction.color)
        return colored_svg
        

def default_instructions_to_SVG():
    """Loads the default set of svg files for instructions."""
    instruction_to_SVG = InstructionToSVG()
    instruction_to_SVG.load.relative_folder(__name__, "SVG-Instructions")
    return instruction_to_SVG

__all__ = ["InstructionToSVG", "default_instructions_to_SVG"]
