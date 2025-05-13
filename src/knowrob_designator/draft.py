import uuid
from typing import List, Tuple, Optional, Dict, Any, Literal

# Define the prefixes
PREFIXES = {
    "SOMA": "<http://www.ease-crc.org/ont/SOMA.owl#>",
    "dul": "<http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#>",
    "rdf": "<http://www.w3.org/1999/02/22-rdf-syntax-ns#>",
    "owl": "<http://www.w3.org/2002/07/owl#>"
}

# Triple type for readability
Triple = Tuple[str, str, str]

def create_individual(class_uri: str, prefix: str = "ind") -> str:
    """
    Create a new individual URI based on class name and a UUID

    Args:
        class_uri: The URI of the class (e.g., "SOMA:PyCramObjectDesignator")
        prefix: A prefix for the individual name

    Returns:
        A URI string for the new individual
    """
    # Extract class name from URI (get everything after the last # or :)
    class_name = class_uri.split('#')[-1] if '#' in class_uri else class_uri.split(':')[-1]

    # Generate UUID
    individual_id = f"{prefix}_{class_name}_{uuid.uuid4().hex[:8]}"

    # Construct URI
    if ":" in class_uri:
        prefix, _ = class_uri.split(":", 1)
        return f"{prefix}:{individual_id}"
    else:
        return f"<{individual_id}>"

def triple(subject: str, predicate: str, object_: str) -> Triple:
    """Helper function to format a triple with proper prefix expansion"""
    for prefix, uri in PREFIXES.items():
        if subject.startswith(f"{prefix}:"):
            subject = subject.replace(f"{prefix}:", f"{uri[:-1]}#")
        if predicate.startswith(f"{prefix}:"):
            predicate = predicate.replace(f"{prefix}:", f"{uri[:-1]}#")
        if object_.startswith(f"{prefix}:"):
            object_ = object_.replace(f"{prefix}:", f"{uri[:-1]}#")

    # Add angle brackets if not present and not a literal
    if not subject.startswith("<") and not subject.startswith('"'):
        subject = f"<{subject}>"
    if not predicate.startswith("<") and not predicate.startswith('"'):
        predicate = f"<{predicate}>"
    if not object_.startswith("<") and not object_.startswith('"') and not object_.startswith("_"):
        object_ = f"<{object_}>"

    return (subject, predicate, object_)

def create_unresolved_designator(
        designator_type: Literal["Object", "Action", "Motion", "Location"],
        description_content: Dict[str, Any]
) -> Tuple[str, List[Triple]]:
    """
    Create an unresolved PyCram designator with all necessary parts

    Args:
        designator_type: Type of designator ("Object", "Action", "Motion", "Location")
        description_content: Key-value pairs for the designator description

    Returns:
        Tuple containing the designator URI and a list of triples
    """
    triples = []

    # Create the designator
    designator_class = f"SOMA:PyCram{designator_type}Designator"
    designator_uri = create_individual(designator_class)

    # Add type triple
    triples.append(triple(designator_uri, "rdf:type", designator_class))

    # Create and link the description
    description_class = f"SOMA:PyCram{designator_type}DesignatorDescription"
    designator_description_uri = create_individual(description_class)

    # Add type triple for description
    triples.append(triple(designator_description_uri, "rdf:type", description_class))

    # Link designator to description
    triples.append(triple(designator_uri, "dul:hasProperPart", designator_description_uri))

    # For each key-value pair in the description content, add appropriate triples
    # This will depend on the designator type and expected structure
    # Here's a simplified approach:

    # First, handle what the description expresses based on designator type
    if designator_type == "Object":
        # Create a Description that describes a PhysicalArtifact
        desc_uri = create_individual("dul:Description")
        triples.append(triple(desc_uri, "rdf:type", "dul:Description"))
        triples.append(triple(designator_description_uri, "dul:expresses", desc_uri))
        # TODO: Add more specific properties based on description_content
        # triples.append(triple(desc_uri, "dul:describes", TODO))

    elif designator_type == "Action":
        # Create a Method
        method_uri = create_individual("dul:Method")
        triples.append(triple(method_uri, "rdf:type", "dul:Method"))
        triples.append(triple(designator_description_uri, "dul:expresses", method_uri))
        # TODO: Add more specific properties based on description_content
        # triples.append(triple(method_uri, "dul:describes", TODO))

    elif designator_type == "Motion":
        # Create a MotionDescription
        motion_desc_uri = create_individual("SOMA:MotionDescription")
        triples.append(triple(motion_desc_uri, "rdf:type", "SOMA:MotionDescription"))
        triples.append(triple(designator_description_uri, "dul:expresses", motion_desc_uri))
        # TODO: Add more specific properties based on description_content
        # triples.append(triple(motion_desc_uri, "dul:describes", TODO))

    elif designator_type == "Location":
        # Create a Description that describes a PhysicalPlace
        desc_uri = create_individual("dul:Description")
        triples.append(triple(desc_uri, "rdf:type", "dul:Description"))
        triples.append(triple(designator_description_uri, "dul:expresses", desc_uri))
        # TODO: Add more specific properties based on description_content
        # triples.append(triple(desc_uri, "dul:describes", TODO))

    # Add description content as data properties
    structured_text_uri = create_individual("SOMA:Structured_Text")
    triples.append(triple(structured_text_uri, "rdf:type", "SOMA:Structured_Text"))


    # Link the description to its structured text representation
    triples.append(triple(designator_description_uri, "SOMA:hasTextRepresentation", structured_text_uri))

    return designator_uri, triples

def create_designator_resolving(
        input_designator_uri: str,
        output_designator_type: Literal["Object", "Action", "Motion", "Location"],
        output_description_content: Dict[str, Any],
        output_referent_content: Dict[str, Any]
) -> Tuple[str, str, List[Triple]]:
    """
    Create a designator resolving task with input and output roles,
    and properly link the output designator's referent to the input designator

    Args:
        input_designator_uri: URI of the input designator
        output_designator_type: Type of the output designator
        output_description_content: Content for the output designator description
        output_referent_content: Content for the output designator referent

    Returns:
        Tuple containing the resolving task URI, output designator URI, and list of triples
    """
    triples = []

    # Create the resolving task
    resolving_uri = create_individual("SOMA:Resolving_of_PyCRAM_Designators")
    triples.append(triple(resolving_uri, "rdf:type", "SOMA:Resolving_of_PyCRAM_Designators"))

    # Create input role (premise)
    premise_uri = create_individual("SOMA:Premise")
    triples.append(triple(premise_uri, "rdf:type", "SOMA:Premise"))
    triples.append(triple(premise_uri, "dul:isRoleOf", input_designator_uri))
    triples.append(triple(resolving_uri, "SOMA:isTaskOfInputRole", premise_uri))

    # Create output designator with description and referent
    output_designator_class = f"SOMA:PyCram{output_designator_type}Designator"
    output_designator_uri = create_individual(output_designator_class)

    # Add type triple
    triples.append(triple(output_designator_uri, "rdf:type", output_designator_class))

    # Create and link the description for output designator
    output_description_class = f"SOMA:PyCram{output_designator_type}DesignatorDescription"
    output_description_uri = create_individual(output_description_class)

    # Add type triple for description
    triples.append(triple(output_description_uri, "rdf:type", output_description_class))

    # Link output designator to description
    triples.append(triple(output_designator_uri, "dul:hasProperPart", output_description_uri))

    # Create and link the referent for output designator
    output_referent_class = f"SOMA:PyCram{output_designator_type}DesignatorReferent"
    output_referent_uri = create_individual(output_referent_class)

    # Add type triple for referent
    triples.append(triple(output_referent_uri, "rdf:type", output_referent_class))

    # Link output designator to referent
    triples.append(triple(output_designator_uri, "dul:hasProperPart", output_referent_uri))

    # TODO Get the description URI of the input designator
    # This requires retrieving it from the knowledge base, but for now we'll infer it
    # by adding "_Description" to the base URI, which isn't correct but illustrates the point
    input_description_uri = input_designator_uri + "_Description"  # Placeholder

    # Now create the appropriate expression relationships based on designator type
    if output_designator_type == "Object":
        # Create a Description that describes a PhysicalArtifact
        output_desc_uri = create_individual("dul:Description")
        triples.append(triple(output_desc_uri, "rdf:type", "dul:Description"))
        triples.append(triple(output_description_uri, "dul:expresses", output_desc_uri))
        # TODO: Add more specific properties based on output_description_content
        # triples.append(triple(referent_desc_uri, "dul:describes", TODO))

        # Create a Description that expands the input description
        referent_desc_uri = create_individual("dul:Description")
        triples.append(triple(referent_desc_uri, "rdf:type", "dul:Description"))
        triples.append(triple(output_referent_uri, "dul:expresses", referent_desc_uri))
        # TODO: Add more specific properties based on referent_description_content
        # triples.append(triple(referent_desc_uri, "dul:describes", TODO))

        # Add expands relationship
        input_expr_uri = create_individual("dul:Description") # TODO get actual URI instead of creating new one
        triples.append(triple(input_expr_uri, "rdf:type", "dul:Description"))
        triples.append(triple(input_expr_uri, "dul:isExpressedBy", input_description_uri))
        triples.append(triple(referent_desc_uri, "dul:expands", input_expr_uri))

    elif output_designator_type == "Action":
        # Create a Method
        method_uri = create_individual("dul:Method")
        triples.append(triple(method_uri, "rdf:type", "dul:Method"))
        triples.append(triple(output_description_uri, "dul:expresses", method_uri))

        # Create a Plan that expands the Method
        plan_uri = create_individual("dul:Plan")
        triples.append(triple(plan_uri, "rdf:type", "dul:Plan"))
        triples.append(triple(output_referent_uri, "dul:expresses", plan_uri))

        # Add expands relationship
        input_method_uri = create_individual("dul:Method") # TODO get actual URI instead of creating new one
        triples.append(triple(input_method_uri, "rdf:type", "dul:Method"))
        triples.append(triple(input_method_uri, "dul:isExpressedBy", input_description_uri))
        triples.append(triple(plan_uri, "dul:expands", input_method_uri))

    elif output_designator_type == "Motion":
        # Create a MotionDescription
        motion_desc_uri = create_individual("SOMA:MotionDescription")
        triples.append(triple(motion_desc_uri, "rdf:type", "SOMA:MotionDescription"))
        triples.append(triple(output_description_uri, "dul:expresses", motion_desc_uri))
        triples.append(triple(output_designator_uri, "dul:expresses", motion_desc_uri))

        # Create a MotionDescription that expands the input MotionDescription
        referent_motion_desc_uri = create_individual("SOMA:MotionDescription")
        triples.append(triple(referent_motion_desc_uri, "rdf:type", "SOMA:MotionDescription"))
        triples.append(triple(output_referent_uri, "dul:expresses", referent_motion_desc_uri))

        # Add expands relationship
        input_motion_desc_uri = create_individual("SOMA:MotionDescription") # TODO get actual URI instead of creating new one
        triples.append(triple(input_motion_desc_uri, "rdf:type", "SOMA:MotionDescription"))
        triples.append(triple(input_motion_desc_uri, "dul:isExpressedBy", input_description_uri))
        triples.append(triple(referent_motion_desc_uri, "dul:expands", input_motion_desc_uri))

    elif output_designator_type == "Location":
        # Create a Description that describes a PhysicalPlace
        output_desc_uri = create_individual("dul:Description")
        triples.append(triple(output_desc_uri, "rdf:type", "dul:Description"))
        triples.append(triple(output_description_uri, "dul:expresses", output_desc_uri))
        triples.append(triple(output_desc_uri, "dul:describes", "dul:PhysicalPlace"))

        # Create a Description that expands the input description
        referent_desc_uri = create_individual("dul:Description")
        triples.append(triple(referent_desc_uri, "rdf:type", "dul:Description"))
        triples.append(triple(output_referent_uri, "dul:expresses", referent_desc_uri))
        triples.append(triple(referent_desc_uri, "dul:describes", "dul:PhysicalPlace"))

        # Add expands relationship
        input_expr_uri = create_individual("dul:Description") # TODO get actual URI instead of creating new one
        triples.append(triple(input_expr_uri, "rdf:type", "dul:Description"))
        triples.append(triple(input_expr_uri, "dul:isExpressedBy", input_description_uri))
        triples.append(triple(referent_desc_uri, "dul:expands", input_expr_uri))

    # Add structured text for output description and referent
    output_desc_text_uri = create_individual("SOMA:Structured_Text")
    triples.append(triple(output_desc_text_uri, "rdf:type", "SOMA:Structured_Text"))

    output_ref_text_uri = create_individual("SOMA:Structured_Text")
    triples.append(triple(output_ref_text_uri, "rdf:type", "SOMA:Structured_Text"))

    # Add directlyDerivedFrom relationships
    triples.append(triple(output_designator_uri, "SOMA:directlyDerivedFrom", input_designator_uri))
    triples.append(triple(output_description_uri, "SOMA:directlyDerivedFrom", input_description_uri))

    # Create output role (conclusion)
    conclusion_uri = create_individual("SOMA:Conclusion")
    triples.append(triple(conclusion_uri, "rdf:type", "SOMA:Conclusion"))
    triples.append(triple(conclusion_uri, "dul:isRoleOf", output_designator_uri))
    triples.append(triple(resolving_uri, "SOMA:isTaskOfOutputRole", conclusion_uri))

    return resolving_uri, output_designator_uri, triples


# Example usage:
if __name__ == "__main__":
    # Example 1: Create an unresolved object designator
    obj_desc = {
        "type": "cup",
        "color": "blue",
        "location": "on table"
    }
    obj_designator_uri, obj_triples = create_unresolved_designator("Object", obj_desc)
    print(f"Created unresolved object designator: {obj_designator_uri}")
    print(f"Generated {len(obj_triples)} triples")

    # Example 2: Create a designator resolving task
    resolved_desc = {
        "type": "cup",
        "color": "blue",
        "location": "on table",
        "size": "medium"
    }
    resolved_ref = {
        "id": "cup_1",
        "position": [0.5, 1.2, 0.8],
        "orientation": [0, 0, 1, 0]
    }

    resolving_uri, resolved_designator_uri, resolving_triples = create_designator_resolving(
        obj_designator_uri, "Object", resolved_desc, resolved_ref
    )

    print(f"Created resolving task: {resolving_uri}")
    print(f"Created resolved designator: {resolved_designator_uri}")
    print(f"Generated {len(resolving_triples)} triples")

    # Print some example triples
    print("\nSample triples:")
    for i, t in enumerate(obj_triples[:5]):
        print(f"{i+1}. {t[0]} {t[1]} {t[2]}")