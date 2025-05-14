import uuid
from typing import List, Tuple, Optional, Dict, Any, Literal

class DesignatorParser:
    # Define the prefixes
    PREFIXES = {
        "SOMA": "<http://www.ease-crc.org/ont/SOMA.owl#>",
        "dul": "<http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#>",
        "rdf": "<http://www.w3.org/1999/02/22-rdf-syntax-ns#>",
        "owl": "<http://www.w3.org/2002/07/owl#>"
    }

    # Triple type for readability
    Triple = Tuple[str, str, str]
    
    # Map from id to last designator uri
    last_designator_id = {}
    # Map from designator uri to designator description uri
    designator_uri_to_description = {}
    # Map from designator uri to referent uri
    designator_uri_to_referent = {}
    # Map from designator uri to designator description description uri
    designator_uri_to_description_description = {}
    # Map from designator uri to task uri
    designator_uri_to_task = {}
    
    # Map CRAM action types to SOMA action types
    action_type_map = {
            "Transporting": "SOMA:Transporting",
            "Manipulating": "SOMA:Manipulating",
            # Add more mappings as needed
     }
    
    def map_action_type_from_cram_to_soma(self, cram_action_type: str) -> str:
        """
        Convert a CRAM action type to a SOMA action type.

        Args:
            cram_action_type: The CRAM action type (e.g., "Transporting")

        Returns:
            The corresponding SOMA action type (e.g., "SOMA:Transporting")
        """
        return self.action_type_map.get(cram_action_type, "SOMA:UnknownAction")

    def create_individual(self, class_uri: str, prefix: str = "ind", id: str = None) -> str:
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

        # If an ID is provided, use it; otherwise, generate a new UUID
        if id:
            individual_id = f"{prefix}_{class_name}_{id}"
        else:
            # Generate a new UUID
            individual_id = f"{prefix}_{class_name}_{uuid.uuid4().hex[:8]}"

        # Construct URI
        if ":" in class_uri:
            prefix, _ = class_uri.split(":", 1)
            return f"{prefix}:{individual_id}"
        else:
            return f"<{individual_id}>"

    def triple(self, subject: str, predicate: str, object_: str) -> Triple:
        """Helper function to format a triple with proper prefix expansion"""
        for prefix, uri in self.PREFIXES.items():
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

    def create_unresolved_designator(self,
            designator_type: Literal["Object", "Action", "Motion", "Location"],
            description_content: Dict[str, Any],
            id: str
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
        designator_uri = self.create_individual(designator_class)
        
        # Store the designator URI for later use
        self.last_designator_id[id] = designator_uri

        # Add type triple
        triples.append(self.triple(designator_uri, "rdf:type", designator_class))
        
        # Add ID triple with soma:hasNameString
        # TODO: Check if self is the correct string syntax. 
        triples.append(self.triple(designator_uri, "SOMA:hasNameString", id))

        # Create and link the description
        description_class = f"SOMA:PyCram{designator_type}DesignatorDescription"
        designator_description_uri = self.create_individual(description_class)
        
        # Store the designator description URI for later use
        self.designator_uri_to_description[designator_uri] = designator_description_uri

        # Add type triple for description
        triples.append(self.triple(designator_description_uri, "rdf:type", description_class))

        # Link designator to description
        triples.append(self.triple(designator_uri, "dul:hasProperPart", designator_description_uri))

        # For each key-value pair in the description content, add appropriate triples
        # self will depend on the designator type and expected structure
        # Here's a simplified approach:

        # First, handle what the description expresses based on designator type
        if designator_type == "Object":
            # Create a Description that describes a PhysicalArtifact
            desc_uri = self.create_individual("dul:Description")
            triples.append(self.triple(desc_uri, "rdf:type", "dul:Description"))
            triples.append(self.triple(designator_description_uri, "dul:expresses", desc_uri))
            # TODO: Add more specific properties based on description_content
            # triples.append(triple(desc_uri, "dul:describes", TODO))

        elif designator_type == "Action":
            # Create a Method
            method_uri = self.create_individual("dul:Method")
            triples.append(self.triple(method_uri, "rdf:type", "dul:Method"))
            triples.append(self.triple(designator_description_uri, "dul:expresses", method_uri))
            # Store the designator description description URI for later use
            self.designator_uri_to_description_description[designator_description_uri] = method_uri
            # From the description content, we extract the type of action
            action_type = description_content.get("type")
            # Map the action type to SOMA
            mapped_action_type = self.map_action_type_from_cram_to_soma(action_type)
            # Create individual for the mapped action type
            mapped_action_type_uri = self.create_individual(mapped_action_type)
            triples.append(self.triple(mapped_action_type_uri, "rdf:type", mapped_action_type))
            triples.append(self.triple(method_uri, "SOMA:isMethodFor", mapped_action_type_uri))
            # Designaor URI to mapped action type URI
            self.designator_uri_to_task[designator_uri] = mapped_action_type_uri
            # TODO: Add more specific properties based on description_content
            # triples.append(triple(method_uri, "dul:describes", TODO))

        elif designator_type == "Motion":
            # Create a MotionDescription
            motion_desc_uri = self.create_individual("SOMA:MotionDescription")
            triples.append(self.triple(motion_desc_uri, "rdf:type", "SOMA:MotionDescription"))
            triples.append(self.triple(designator_description_uri, "dul:expresses", motion_desc_uri))
            # TODO: Add more specific properties based on description_content
            # triples.append(triple(motion_desc_uri, "dul:describes", TODO))

        elif designator_type == "Location":
            # Create a Description that describes a PhysicalPlace
            desc_uri = self.create_individual("dul:Description")
            triples.append(self.triple(desc_uri, "rdf:type", "dul:Description"))
            triples.append(self.triple(designator_description_uri, "dul:expresses", desc_uri))
            # TODO: Add more specific properties based on description_content
            # triples.append(triple(desc_uri, "dul:describes", TODO))

        return designator_uri, triples

    def create_designator_resolving(self,
            input_designator_id: str,
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
        
        # Create the input designator URI
        input_designator_uri = self.last_designator_id[input_designator_id]

        # Create the resolving task
        resolving_uri = self.create_individual("SOMA:Resolving_of_PyCRAM_Designators")
        triples.append(self.triple(resolving_uri, "rdf:type", "SOMA:Resolving_of_PyCRAM_Designators"))

        # Create input role (premise)
        premise_uri = self.create_individual("SOMA:Premise")
        triples.append(self.triple(premise_uri, "rdf:type", "SOMA:Premise"))
        triples.append(self.triple(premise_uri, "dul:isRoleOf", input_designator_uri))
        triples.append(self.triple(resolving_uri, "SOMA:isTaskOfInputRole", premise_uri))

        # Create output designator with description and referent
        output_designator_class = f"SOMA:PyCram{output_designator_type}Designator"
        output_designator_uri = self.create_individual(output_designator_class)

        # Add type triple
        triples.append(self.triple(output_designator_uri, "rdf:type", output_designator_class))

        # Create and link the description for output designator
        output_description_class = f"SOMA:PyCram{output_designator_type}DesignatorDescription"
        output_description_uri = self.create_individual(output_description_class)

        # Add type triple for description
        triples.append(self.triple(output_description_uri, "rdf:type", output_description_class))

        # Link output designator to description
        triples.append(self.triple(output_designator_uri, "dul:hasProperPart", output_description_uri))

        # Create and link the referent for output designator
        output_referent_class = f"SOMA:PyCram{output_designator_type}DesignatorReferent"
        output_referent_uri = self.create_individual(output_referent_class)

        # Add type triple for referent
        triples.append(self.triple(output_referent_uri, "rdf:type", output_referent_class))

        # Link output designator to referent
        triples.append(self.triple(output_designator_uri, "dul:hasProperPart", output_referent_uri))

        # Retrieve the input designator description URI
        input_description_uri = self.designator_uri_to_description[input_designator_uri]

        # Now create the appropriate expression relationships based on designator type
        if output_designator_type == "Object":
            # Create a Description that describes a PhysicalArtifact
            output_desc_uri = self.create_individual("dul:Description")
            triples.append(self.triple(output_desc_uri, "rdf:type", "dul:Description"))
            triples.append(self.triple(output_description_uri, "dul:expresses", output_desc_uri))
            # Store the designator description description URI for later use
            self.designator_uri_to_description_description[output_designator_uri] = output_desc_uri
            # TODO: Add more specific properties based on output_description_content
            # triples.append(triple(referent_desc_uri, "dul:describes", TODO))

        elif output_designator_type == "Action":            
            # Create a Method
            plan_uri = self.create_individual("dul:Plan")
            triples.append(self.triple(plan_uri, "rdf:type", "dul:Plan"))
            triples.append(self.triple(output_description_uri, "dul:expresses", plan_uri))
            
            # Store the designator description description URI for later use
            self.designator_uri_to_description_description[output_designator_uri] = plan_uri
            # From the description content, we extract the type of action
            action_type = output_description_content.get("type")
            # Map the action type to SOMA
            mapped_action_type = self.map_action_type_from_cram_to_soma(action_type)
            # Create individual for the mapped action type
            mapped_action_type_uri = self.create_individual(mapped_action_type)
            triples.append(self.triple(mapped_action_type_uri, "rdf:type", mapped_action_type))
            triples.append(self.triple(plan_uri, "SOMA:isPlanFor", mapped_action_type_uri))
            # Designator URI to mapped action type URI
            self.designator_uri_to_task[output_designator_uri] = mapped_action_type_uri

            # Create a Plan that expands the Method
            plan_uri = self.create_individual("dul:Plan")
            triples.append(self.triple(plan_uri, "rdf:type", "dul:Plan"))
            triples.append(self.triple(output_referent_uri, "dul:expresses", plan_uri))
            
        elif output_designator_type == "Motion":
            # Create a MotionDescription
            motion_desc_uri = self.create_individual("SOMA:MotionDescription")
            triples.append(self.triple(motion_desc_uri, "rdf:type", "SOMA:MotionDescription"))
            triples.append(self.triple(output_description_uri, "dul:expresses", motion_desc_uri))
            triples.append(self.triple(output_designator_uri, "dul:expresses", motion_desc_uri))

            # Create a MotionDescription that expands the input MotionDescription
            referent_motion_desc_uri = self.create_individual("SOMA:MotionDescription")
            triples.append(self.triple(referent_motion_desc_uri, "rdf:type", "SOMA:MotionDescription"))
            triples.append(self.triple(output_referent_uri, "dul:expresses", referent_motion_desc_uri))

        elif output_designator_type == "Location":
            # Create a Description that describes a PhysicalPlace
            output_desc_uri = self.create_individual("dul:Description")
            triples.append(self.triple(output_desc_uri, "rdf:type", "dul:Description"))
            triples.append(self.triple(output_description_uri, "dul:expresses", output_desc_uri))
            triples.append(self.triple(output_desc_uri, "dul:describes", "dul:PhysicalPlace"))

            # Create a Description that expands the input description
            referent_desc_uri = self.create_individual("dul:Description")
            triples.append(self.triple(referent_desc_uri, "rdf:type", "dul:Description"))
            triples.append(self.triple(output_referent_uri, "dul:expresses", referent_desc_uri))
            triples.append(self.triple(referent_desc_uri, "dul:describes", "dul:PhysicalPlace"))

        # Add expands relationship
        triples.append(self.triple(referent_desc_uri, "dul:expands", output_desc_uri))
        # Get designator description description URI
        input_desc_desc_uri = self.designator_uri_to_description_description[input_description_uri]
        triples.append(self.triple(referent_desc_uri, "dul:expands", input_desc_desc_uri))
        # TODO: If there are multiple resolving tasks, each referent description expands the previous referent description (also for the other designator types)

        # Add directlyDerivedFrom relationships
        triples.append(self.triple(output_designator_uri, "SOMA:directlyDerivedFrom", input_designator_uri))
        triples.append(self.triple(output_description_uri, "SOMA:directlyDerivedFrom", input_description_uri))

        # Create output role (conclusion)
        conclusion_uri = self.create_individual("SOMA:Conclusion")
        triples.append(self.triple(conclusion_uri, "rdf:type", "SOMA:Conclusion"))
        triples.append(self.triple(conclusion_uri, "dul:isRoleOf", output_designator_uri))
        triples.append(self.triple(resolving_uri, "SOMA:isTaskOfOutputRole", conclusion_uri))

        return resolving_uri, output_designator_uri, triples


# Example usage:
if __name__ == "__main__":
    # Initialize the DesignatorParser
    parser = DesignatorParser()
    # Example 1: Create an unresolved object designator
    obj_desc = {
        "type": "cup",
        "color": "blue",
        "location": "on table"
    }
    obj_designator_uri, obj_triples = parser.create_unresolved_designator("Object", obj_desc, id="234234234")
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

    resolving_uri, resolved_designator_uri, resolving_triples = parser.create_designator_resolving(
        obj_designator_uri, "Object", resolved_desc, resolved_ref
    )

    print(f"Created resolving task: {resolving_uri}")
    print(f"Created resolved designator: {resolved_designator_uri}")
    print(f"Generated {len(resolving_triples)} triples")

    # Print some example triples
    print("\nSample triples:")
    for i, t in enumerate(obj_triples[:5]):
        print(f"{i+1}. {t[0]} {t[1]} {t[2]}")