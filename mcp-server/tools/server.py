from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import uvicorn
import json
import logging
import asyncio
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="QCYIS MCP Server",
    description="Model Context Protocol Server for Yoga Intelligence Tools",
    version="1.0.0"
)

# Pydantic models for request/response
class PoseAnalysisRequest(BaseModel):
    landmarks: List[Dict[str, float]]
    pose_type: str
    duration: Optional[float] = 0

class BreathingRequest(BaseModel):
    pattern: str = "4-7-8"
    duration: int = 300  # seconds

class MeditationRequest(BaseModel):
    theme: str = "mindfulness"
    duration: int = 600  # seconds
    level: str = "beginner"

class RoutineRequest(BaseModel):
    level: str = "beginner"
    duration: int = 30  # minutes
    focus: str = "general"
    limitations: List[str] = []

class ToolResponse(BaseModel):
    success: bool
    data: Any
    message: str

# Yoga pose reference database
POSE_REFERENCES = {
    "mountain": {
        "description": "Standing tall with feet hip-width apart",
        "benefits": ["Improves posture", "Builds strength", "Enhances balance"],
        "alignment": {
            "feet": "Hip-width apart, parallel",
            "legs": "Strong and straight",
            "spine": "Long and neutral",
            "arms": "At sides, palms facing forward"
        }
    },
    "warrior_1": {
        "description": "Standing lunge with arms overhead",
        "benefits": ["Strengthens legs", "Opens hips", "Improves balance"],
        "alignment": {
            "front_leg": "Bent at 90 degrees",
            "back_leg": "Straight and strong",
            "hips": "Square to front",
            "arms": "Reaching up"
        }
    },
    "downward_dog": {
        "description": "Inverted V-shape pose",
        "benefits": ["Strengthens arms", "Stretches hamstrings", "Energizes body"],
        "alignment": {
            "hands": "Shoulder-width apart",
            "feet": "Hip-width apart",
            "spine": "Long and straight",
            "head": "Between arms"
        }
    }
}

# Breathing patterns database
BREATHING_PATTERNS = {
    "4-7-8": {
        "inhale": 4,
        "hold": 7,
        "exhale": 8,
        "description": "Calming breath for relaxation"
    },
    "box": {
        "inhale": 4,
        "hold": 4,
        "exhale": 4,
        "hold": 4,
        "description": "Balanced breath for focus"
    },
    "ujjayi": {
        "inhale": 6,
        "exhale": 6,
        "description": "Ocean breath for yoga practice"
    }
}

@app.get("/")
async def root():
    return {"message": "QCYIS MCP Server is running", "version": "1.0.0"}

@app.post("/tools/analyze_pose", response_model=ToolResponse)
async def analyze_pose(request: PoseAnalysisRequest):
    """Analyze yoga pose and provide detailed feedback"""
    try:
        pose_type = request.pose_type.lower()
        landmarks = request.landmarks
        
        if pose_type not in POSE_REFERENCES:
            pose_type = "general_pose"
        
        # Calculate pose quality (simplified)
        quality_score = await calculate_pose_quality(landmarks, pose_type)
        
        # Generate corrections
        corrections = await generate_pose_corrections(landmarks, pose_type)
        
        # Get pose information
        pose_info = POSE_REFERENCES.get(pose_type, {})
        
        analysis_result = {
            "pose_type": pose_type,
            "quality_score": quality_score,
            "corrections": corrections,
            "pose_info": pose_info,
            "timestamp": datetime.now().isoformat()
        }
        
        return ToolResponse(
            success=True,
            data=analysis_result,
            message=f"Pose analysis completed for {pose_type}"
        )
        
    except Exception as e:
        logger.error(f"Pose analysis error: {e}")
        return ToolResponse(
            success=False,
            data={},
            message=f"Analysis failed: {str(e)}"
        )

@app.post("/tools/breathing_guide", response_model=ToolResponse)
async def breathing_guide(request: BreathingRequest):
    """Generate breathing exercise instructions"""
    try:
        pattern = request.pattern.lower()
        duration = request.duration
        
        if pattern not in BREATHING_PATTERNS:
            pattern = "4-7-8"
        
        breath_pattern = BREATHING_PATTERNS[pattern]
        cycles = duration // sum([v for k, v in breath_pattern.items() if isinstance(v, int)])
        
        instructions = {
            "pattern": pattern,
            "description": breath_pattern["description"],
            "duration_seconds": duration,
            "estimated_cycles": cycles,
            "instructions": await generate_breathing_instructions(breath_pattern, cycles),
            "benefits": await get_breathing_benefits(pattern)
        }
        
        return ToolResponse(
            success=True,
            data=instructions,
            message=f"Breathing guide generated for {pattern} pattern"
        )
        
    except Exception as e:
        logger.error(f"Breathing guide error: {e}")
        return ToolResponse(
            success=False,
            data={},
            message=f"Guide generation failed: {str(e)}"
        )

@app.post("/tools/meditation_prompt", response_model=ToolResponse)
async def meditation_prompt(request: MeditationRequest):
    """Generate meditation guidance and prompts"""
    try:
        theme = request.theme.lower()
        duration = request.duration
        level = request.level.lower()
        
        meditation_guide = await generate_meditation_guide(theme, duration, level)
        
        return ToolResponse(
            success=True,
            data=meditation_guide,
            message=f"Meditation prompt generated for {theme} theme"
        )
        
    except Exception as e:
        logger.error(f"Meditation prompt error: {e}")
        return ToolResponse(
            success=False,
            data={},
            message=f"Prompt generation failed: {str(e)}"
        )

@app.post("/tools/generate_routine", response_model=ToolResponse)
async def generate_routine(request: RoutineRequest):
    """Generate personalized yoga routine"""
    try:
        routine = await create_yoga_routine(
            level=request.level,
            duration=request.duration,
            focus=request.focus,
            limitations=request.limitations
        )
        
        return ToolResponse(
            success=True,
            data=routine,
            message=f"Yoga routine generated for {request.level} level"
        )
        
    except Exception as e:
        logger.error(f"Routine generation error: {e}")
        return ToolResponse(
            success=False,
            data={},
            message=f"Routine generation failed: {str(e)}"
        )

@app.get("/tools/pose_library")
async def get_pose_library():
    """Get complete pose library with descriptions"""
    return ToolResponse(
        success=True,
        data=POSE_REFERENCES,
        message="Pose library retrieved successfully"
    )

@app.get("/tools/breathing_patterns")
async def get_breathing_patterns():
    """Get available breathing patterns"""
    return ToolResponse(
        success=True,
        data=BREATHING_PATTERNS,
        message="Breathing patterns retrieved successfully"
    )

# Helper functions
async def calculate_pose_quality(landmarks: List[Dict], pose_type: str) -> float:
    """Calculate pose quality score based on landmarks"""
    if not landmarks:
        return 0.0
    
    # Simplified quality calculation
    base_score = 75.0
    
    # Add randomness for demonstration
    import random
    variation = random.uniform(-15, 25)
    quality = max(0, min(100, base_score + variation))
    
    return round(quality, 1)

async def generate_pose_corrections(landmarks: List[Dict], pose_type: str) -> List[str]:
    """Generate pose correction suggestions"""
    corrections = []
    
    if pose_type == "mountain":
        corrections = [
            "Engage your core muscles",
            "Lengthen through the crown of your head",
            "Relax your shoulders away from your ears"
        ]
    elif pose_type == "warrior_1":
        corrections = [
            "Square your hips toward the front",
            "Bend your front knee to 90 degrees",
            "Keep your back leg straight and strong"
        ]
    elif pose_type == "downward_dog":
        corrections = [
            "Press firmly through your hands",
            "Lengthen your spine",
            "Pedal your feet to stretch your calves"
        ]
    else:
        corrections = [
            "Focus on your breath",
            "Maintain steady alignment",
            "Listen to your body"
        ]
    
    return corrections

async def generate_breathing_instructions(pattern: Dict, cycles: int) -> List[str]:
    """Generate step-by-step breathing instructions"""
    instructions = [
        "Find a comfortable seated position",
        "Close your eyes or soften your gaze",
        "Begin with natural breathing to center yourself"
    ]
    
    if "inhale" in pattern and "exhale" in pattern:
        if "hold" in pattern:
            instructions.extend([
                f"Inhale for {pattern['inhale']} counts",
                f"Hold for {pattern['hold']} counts",
                f"Exhale for {pattern['exhale']} counts",
                f"Repeat for {cycles} cycles"
            ])
        else:
            instructions.extend([
                f"Inhale for {pattern['inhale']} counts",
                f"Exhale for {pattern['exhale']} counts",
                f"Repeat for {cycles} cycles"
            ])
    
    instructions.append("Return to natural breathing when complete")
    return instructions

async def get_breathing_benefits(pattern: str) -> List[str]:
    """Get benefits of specific breathing pattern"""
    benefits = {
        "4-7-8": [
            "Reduces anxiety and stress",
            "Promotes better sleep",
            "Calms the nervous system"
        ],
        "box": [
            "Improves focus and concentration",
            "Balances the nervous system",
            "Enhances mental clarity"
        ],
        "ujjayi": [
            "Builds internal heat",
            "Maintains focus during yoga",
            "Calms the mind"
        ]
    }
    return benefits.get(pattern, ["Promotes relaxation", "Improves breath awareness"])

async def generate_meditation_guide(theme: str, duration: int, level: str) -> Dict:
    """Generate comprehensive meditation guide"""
    guides = {
        "mindfulness": {
            "introduction": "Focus on present moment awareness",
            "technique": "Observe thoughts without judgment",
            "anchor": "Breath or body sensations"
        },
        "loving_kindness": {
            "introduction": "Cultivate compassion and love",
            "technique": "Send loving wishes to yourself and others",
            "anchor": "Heart center and loving phrases"
        },
        "body_scan": {
            "introduction": "Systematic awareness of the body",
            "technique": "Move attention through each body part",
            "anchor": "Physical sensations"
        }
    }
    
    guide = guides.get(theme, guides["mindfulness"])
    
    return {
        "theme": theme,
        "duration_minutes": duration // 60,
        "level": level,
        "introduction": guide["introduction"],
        "technique": guide["technique"],
        "anchor": guide["anchor"],
        "steps": await generate_meditation_steps(theme, duration, level),
        "closing": "Gently return awareness to your surroundings"
    }

async def generate_meditation_steps(theme: str, duration: int, level: str) -> List[str]:
    """Generate meditation steps based on theme and level"""
    base_steps = [
        "Settle into a comfortable position",
        "Close your eyes and take three deep breaths",
        "Begin to notice your natural breathing rhythm"
    ]
    
    if theme == "mindfulness":
        base_steps.extend([
            "When thoughts arise, simply notice them",
            "Gently return attention to your breath",
            "Continue observing with kind awareness"
        ])
    elif theme == "loving_kindness":
        base_steps.extend([
            "Place hand on heart and feel its rhythm",
            "Silently repeat: 'May I be happy and peaceful'",
            "Extend these wishes to loved ones, then all beings"
        ])
    elif theme == "body_scan":
        base_steps.extend([
            "Start by noticing the top of your head",
            "Slowly move attention down through your body",
            "Notice sensations without trying to change them"
        ])
    
    return base_steps

async def create_yoga_routine(level: str, duration: int, focus: str, limitations: List[str]) -> Dict:
    """Create personalized yoga routine"""
    routines = {
        "beginner": {
            "warm_up": ["Mountain Pose", "Arm Circles", "Neck Rolls"],
            "main_poses": ["Cat-Cow", "Downward Dog", "Child's Pose", "Warrior I"],
            "cool_down": ["Seated Forward Fold", "Supine Twist", "Savasana"]
        },
        "intermediate": {
            "warm_up": ["Sun Salutation A", "Standing Forward Fold"],
            "main_poses": ["Warrior II", "Triangle Pose", "Tree Pose", "Bridge Pose"],
            "cool_down": ["Pigeon Pose", "Happy Baby", "Savasana"]
        },
        "advanced": {
            "warm_up": ["Sun Salutation B", "Standing Poses Flow"],
            "main_poses": ["Crow Pose", "Headstand Prep", "Wheel Pose", "Eagle Pose"],
            "cool_down": ["King Pigeon", "Lotus Prep", "Meditation"]
        }
    }
    
    routine = routines.get(level, routines["beginner"])
    
    return {
        "level": level,
        "duration_minutes": duration,
        "focus": focus,
        "limitations_considered": limitations,
        "warm_up": routine["warm_up"],
        "main_sequence": routine["main_poses"],
        "cool_down": routine["cool_down"],
        "estimated_timing": {
            "warm_up": duration * 0.2,
            "main_sequence": duration * 0.6,
            "cool_down": duration * 0.2
        },
        "modifications": await get_modifications_for_limitations(limitations)
    }

async def get_modifications_for_limitations(limitations: List[str]) -> Dict[str, str]:
    """Get pose modifications based on limitations"""
    modifications = {}
    
    for limitation in limitations:
        if "knee" in limitation.lower():
            modifications["knee_issues"] = "Use props, avoid deep lunges"
        elif "back" in limitation.lower():
            modifications["back_issues"] = "Avoid deep backbends, use support"
        elif "wrist" in limitation.lower():
            modifications["wrist_issues"] = "Use fists or forearms instead of palms"
        elif "neck" in limitation.lower():
            modifications["neck_issues"] = "Avoid inversions, keep head neutral"
    
    return modifications

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8033, log_level="info")
