"""
Default Markov Chain definitions.

This module provides pre-configured Markov chain definitions for different
user behavior scenarios to help users get started quickly.

Each chain models a different pattern of user behavior that can be simulated.
"""

import logging
from typing import Dict, List, Any, Optional
from uuid import UUID

from app.models.markov import MarkovChain, State
from app.database import Database

logger = logging.getLogger(__name__)

# E-commerce user journey
ECOMMERCE_CHAIN = {
    "name": "E-commerce User Journey",
    "description": "A realistic simulation of user behavior on an e-commerce website",
    "states": {
        "homepage": {
            "name": "homepage",
            "transitions": {
                "category_listing": 0.35,
                "product_search": 0.25,
                "login": 0.15,
                "featured_product": 0.15,
                "cart": 0.05,
                "account": 0.05
            },
            "http_method": "GET",
            "payload": {}
        },
        "category_listing": {
            "name": "category_listing",
            "transitions": {
                "product_listing": 0.6,
                "category_filter": 0.2,
                "homepage": 0.1,
                "search_results": 0.1
            },
            "http_method": "GET",
            "payload": {"category_id": 123}
        },
        "category_filter": {
            "name": "category_filter",
            "transitions": {
                "product_listing": 0.7,
                "category_listing": 0.2,
                "homepage": 0.1
            },
            "http_method": "GET",
            "payload": {"category_id": 123, "filter": {"price_range": "100-200", "brand": "acme"}}
        },
        "product_listing": {
            "name": "product_listing",
            "transitions": {
                "product_detail": 0.6,
                "category_filter": 0.15,
                "category_listing": 0.1,
                "homepage": 0.05,
                "cart": 0.1
            },
            "http_method": "GET",
            "payload": {"page": 1, "sort": "popularity"}
        },
        "product_detail": {
            "name": "product_detail",
            "transitions": {
                "add_to_cart": 0.3,
                "product_reviews": 0.2,
                "product_listing": 0.2,
                "add_to_wishlist": 0.1,
                "homepage": 0.1,
                "related_product": 0.1
            },
            "http_method": "GET",
            "payload": {"product_id": 1234}
        },
        "product_reviews": {
            "name": "product_reviews",
            "transitions": {
                "product_detail": 0.6,
                "write_review": 0.1,
                "product_listing": 0.2,
                "homepage": 0.1
            },
            "http_method": "GET",
            "payload": {"product_id": 1234, "page": 1}
        },
        "related_product": {
            "name": "related_product",
            "transitions": {
                "product_detail": 0.7,
                "add_to_cart": 0.2,
                "product_listing": 0.1
            },
            "http_method": "GET",
            "payload": {"product_id": 5678}
        },
        "add_to_wishlist": {
            "name": "add_to_wishlist",
            "transitions": {
                "product_detail": 0.7,
                "wishlist": 0.2,
                "product_listing": 0.1
            },
            "http_method": "POST",
            "payload": {"product_id": 1234}
        },
        "wishlist": {
            "name": "wishlist",
            "transitions": {
                "product_detail": 0.4,
                "account": 0.3,
                "homepage": 0.3
            },
            "http_method": "GET",
            "payload": {}
        },
        "write_review": {
            "name": "write_review",
            "transitions": {
                "product_detail": 0.5,
                "product_reviews": 0.3,
                "homepage": 0.2
            },
            "http_method": "POST",
            "payload": {"product_id": 1234, "rating": 5, "comment": "Great product!"}
        },
        "add_to_cart": {
            "name": "add_to_cart",
            "transitions": {
                "cart": 0.4,
                "product_detail": 0.3,
                "checkout": 0.2,
                "product_listing": 0.1
            },
            "http_method": "POST",
            "payload": {"product_id": 1234, "quantity": 1}
        },
        "cart": {
            "name": "cart",
            "transitions": {
                "checkout": 0.4,
                "product_detail": 0.2,
                "update_cart": 0.2,
                "homepage": 0.1,
                "product_listing": 0.1
            },
            "http_method": "GET",
            "payload": {}
        },
        "update_cart": {
            "name": "update_cart",
            "transitions": {
                "cart": 0.8,
                "checkout": 0.2
            },
            "http_method": "PATCH",
            "payload": {"item_id": 5678, "quantity": 2}
        },
        "checkout": {
            "name": "checkout",
            "transitions": {
                "payment": 0.6,
                "cart": 0.3,
                "homepage": 0.1
            },
            "http_method": "GET",
            "payload": {}
        },
        "payment": {
            "name": "payment",
            "transitions": {
                "order_confirmation": 0.7,
                "checkout": 0.2,
                "cart": 0.1
            },
            "http_method": "POST",
            "payload": {"payment_method": "credit_card", "amount": 99.99}
        },
        "order_confirmation": {
            "name": "order_confirmation",
            "transitions": {
                "homepage": 0.5,
                "account_orders": 0.3,
                "product_listing": 0.2
            },
            "http_method": "GET",
            "payload": {"order_id": "ORD-12345"}
        },
        "product_search": {
            "name": "product_search",
            "transitions": {
                "search_results": 0.8,
                "homepage": 0.2
            },
            "http_method": "POST",
            "payload": {"query": "smartphone", "filters": {}}
        },
        "search_results": {
            "name": "search_results",
            "transitions": {
                "product_detail": 0.5,
                "product_listing": 0.3,
                "homepage": 0.2
            },
            "http_method": "GET",
            "payload": {"query": "smartphone", "page": 1}
        },
        "login": {
            "name": "login",
            "transitions": {
                "homepage": 0.4,
                "account": 0.3,
                "cart": 0.2,
                "register": 0.1
            },
            "http_method": "POST",
            "payload": {"email": "user@example.com", "password": "********"}
        },
        "account": {
            "name": "account",
            "transitions": {
                "homepage": 0.6,
                "cart": 0.4
            },
            "http_method": "GET",
            "payload": {}
        },
        "account_orders": {
            "name": "account_orders",
            "transitions": {
                "order_details": 0.4,
                "account": 0.3,
                "homepage": 0.3
            },
            "http_method": "GET",
            "payload": {}
        },
        "order_details": {
            "name": "order_details",
            "transitions": {
                "account_orders": 0.6,
                "write_review": 0.2,
                "account": 0.2
            },
            "http_method": "GET",
            "payload": {"order_id": "ORD-12345"}
        },
        "featured_product": {
            "name": "featured_product",
            "transitions": {
                "product_detail": 0.7,
                "homepage": 0.2,
                "add_to_cart": 0.1
            },
            "http_method": "GET",
            "payload": {"product_id": 9012}
        },
        "register": {
            "name": "register",
            "transitions": {
                "homepage": 0.5,
                "account": 0.3,
                "login": 0.2
            },
            "http_method": "POST",
            "payload": {
                "email": "newuser@example.com",
                "password": "********",
                "name": "New User"
            }
        }
    },
    "initial_state": "homepage"
}

# Social media user behavior
SOCIAL_MEDIA_CHAIN = {
    "name": "Social Media Interactions",
    "description": "Simulates typical user interactions on a social media platform",
    "states": {
        "feed": {
            "name": "feed",
            "transitions": {
                "view_post": 0.4,
                "profile": 0.2,
                "notifications": 0.2,
                "search": 0.1,
                "messages": 0.1
            },
            "http_method": "GET",
            "payload": {}
        },
        "view_post": {
            "name": "view_post",
            "transitions": {
                "like_post": 0.3,
                "comment": 0.2,
                "share_post": 0.1,
                "user_profile": 0.2,
                "feed": 0.2
            },
            "http_method": "GET",
            "payload": {"post_id": 12345}
        },
        "like_post": {
            "name": "like_post",
            "transitions": {
                "view_post": 0.4,
                "comment": 0.2,
                "feed": 0.4
            },
            "http_method": "POST",
            "payload": {"post_id": 12345, "action": "like"}
        },
        "comment": {
            "name": "comment",
            "transitions": {
                "view_post": 0.6,
                "feed": 0.4
            },
            "http_method": "POST",
            "payload": {"post_id": 12345, "content": "Great post!"}
        },
        "share_post": {
            "name": "share_post",
            "transitions": {
                "view_post": 0.3,
                "feed": 0.7
            },
            "http_method": "POST",
            "payload": {"post_id": 12345, "share_type": "timeline"}
        },
        "user_profile": {
            "name": "user_profile",
            "transitions": {
                "view_post": 0.3,
                "follow_user": 0.2,
                "messages": 0.1,
                "feed": 0.4
            },
            "http_method": "GET",
            "payload": {"user_id": 5678}
        },
        "follow_user": {
            "name": "follow_user",
            "transitions": {
                "user_profile": 0.6,
                "feed": 0.4
            },
            "http_method": "POST",
            "payload": {"user_id": 5678, "action": "follow"}
        },
        "profile": {
            "name": "profile",
            "transitions": {
                "edit_profile": 0.2,
                "view_post": 0.3,
                "feed": 0.5
            },
            "http_method": "GET",
            "payload": {}
        },
        "edit_profile": {
            "name": "edit_profile",
            "transitions": {
                "profile": 0.7,
                "feed": 0.3
            },
            "http_method": "PATCH",
            "payload": {"bio": "Updated bio", "avatar_url": "https://example.com/avatar.jpg"}
        },
        "notifications": {
            "name": "notifications",
            "transitions": {
                "view_post": 0.4,
                "user_profile": 0.2,
                "feed": 0.4
            },
            "http_method": "GET",
            "payload": {}
        },
        "messages": {
            "name": "messages",
            "transitions": {
                "conversation": 0.6,
                "feed": 0.4
            },
            "http_method": "GET",
            "payload": {}
        },
        "conversation": {
            "name": "conversation",
            "transitions": {
                "send_message": 0.7,
                "messages": 0.2,
                "feed": 0.1
            },
            "http_method": "GET",
            "payload": {"conversation_id": 9876}
        },
        "send_message": {
            "name": "send_message",
            "transitions": {
                "conversation": 0.8,
                "messages": 0.1,
                "feed": 0.1
            },
            "http_method": "POST",
            "payload": {"conversation_id": 9876, "content": "Hello there!"}
        },
        "search": {
            "name": "search",
            "transitions": {
                "user_profile": 0.4,
                "view_post": 0.3,
                "feed": 0.3
            },
            "http_method": "GET",
            "payload": {"query": "example search"}
        }
    },
    "initial_state": "feed"
}

# Content streaming platform behavior
STREAMING_PLATFORM_CHAIN = {
    "name": "Content Streaming Platform",
    "description": "Models how users interact with video/music streaming services",
    "states": {
        "browse_home": {
            "name": "browse_home",
            "transitions": {
                "browse_category": 0.3,
                "search_content": 0.2,
                "view_content": 0.3,
                "user_account": 0.1,
                "recommendations": 0.1
            },
            "http_method": "GET",
            "payload": {}
        },
        "browse_category": {
            "name": "browse_category",
            "transitions": {
                "view_content": 0.5,
                "browse_home": 0.3,
                "search_content": 0.2
            },
            "http_method": "GET",
            "payload": {"category": "action"}
        },
        "search_content": {
            "name": "search_content",
            "transitions": {
                "view_content": 0.6,
                "browse_home": 0.3,
                "browse_category": 0.1
            },
            "http_method": "GET",
            "payload": {"query": "popular movies"}
        },
        "view_content": {
            "name": "view_content",
            "transitions": {
                "play_content": 0.6,
                "rate_content": 0.1,
                "add_to_list": 0.1,
                "browse_home": 0.1,
                "recommendations": 0.1
            },
            "http_method": "GET",
            "payload": {"content_id": "movie123"}
        },
        "play_content": {
            "name": "play_content",
            "transitions": {
                "rate_content": 0.2,
                "view_content": 0.3,
                "recommendations": 0.2,
                "browse_home": 0.3
            },
            "http_method": "POST",
            "payload": {"content_id": "movie123", "timestamp": 0}
        },
        "rate_content": {
            "name": "rate_content",
            "transitions": {
                "view_content": 0.4,
                "browse_home": 0.3,
                "recommendations": 0.3
            },
            "http_method": "POST",
            "payload": {"content_id": "movie123", "rating": 4}
        },
        "add_to_list": {
            "name": "add_to_list",
            "transitions": {
                "view_content": 0.4,
                "browse_home": 0.4,
                "view_my_list": 0.2
            },
            "http_method": "POST",
            "payload": {"content_id": "movie123", "list": "watch_later"}
        },
        "view_my_list": {
            "name": "view_my_list",
            "transitions": {
                "view_content": 0.6,
                "browse_home": 0.3,
                "user_account": 0.1
            },
            "http_method": "GET",
            "payload": {}
        },
        "recommendations": {
            "name": "recommendations",
            "transitions": {
                "view_content": 0.7,
                "browse_home": 0.3
            },
            "http_method": "GET",
            "payload": {"based_on": "movie123"}
        },
        "user_account": {
            "name": "user_account",
            "transitions": {
                "view_my_list": 0.3,
                "subscription_settings": 0.2,
                "browse_home": 0.5
            },
            "http_method": "GET",
            "payload": {}
        },
        "subscription_settings": {
            "name": "subscription_settings",
            "transitions": {
                "update_subscription": 0.3,
                "user_account": 0.4,
                "browse_home": 0.3
            },
            "http_method": "GET",
            "payload": {}
        },
        "update_subscription": {
            "name": "update_subscription",
            "transitions": {
                "subscription_settings": 0.5,
                "user_account": 0.3,
                "browse_home": 0.2
            },
            "http_method": "PATCH",
            "payload": {"plan": "premium", "payment_method": "credit_card"}
        }
    },
    "initial_state": "browse_home"
}

# Dictionary of all available default chains
DEFAULT_CHAINS = {
    "ecommerce": ECOMMERCE_CHAIN,
    "social_media": SOCIAL_MEDIA_CHAIN,
    "streaming": STREAMING_PLATFORM_CHAIN
}

# Dictionary to store created chain IDs for easy access
default_chain_ids = {}


async def create_default_markov_chains() -> Dict[str, UUID]:
    """
    Create all default Markov chains if none exist.
    
    Returns:
        Dictionary mapping chain keys to their UUIDs
    """
    global default_chain_ids
    
    chains = await Database.get_all_markov_chains()
    logger.info(f"Found {len(chains)} existing Markov chain(s)")
    
    if not chains:
        logger.info("No existing Markov chains found. Creating default chains...")
        
        for key, chain_dict in DEFAULT_CHAINS.items():
            try:
                # Convert the dictionary to a MarkovChain model
                states_dict = {}
                for state_name, state_data in chain_dict["states"].items():
                    states_dict[state_name] = State(**state_data)
                
                chain = MarkovChain(
                    states=states_dict,
                    initial_state=chain_dict["initial_state"],
                    name=chain_dict["name"],
                    description=chain_dict["description"]
                )
                
                # Create the chain in the database
                created_chain = await Database.create_markov_chain(chain)
                default_chain_ids[key] = created_chain.id
                
                logger.info(f"✅ Created default {key} Markov chain with ID: {created_chain.id}")
                logger.info(f"Chain contains {len(chain.states)} states")
                
                # Verify it's retrievable
                retrieved_chain = await Database.get_markov_chain(created_chain.id)
                assert retrieved_chain is not None, f"Failed to retrieve newly created chain with ID: {created_chain.id}"
                    
            except Exception as e:
                logger.error(f"❌ Failed to create {key} Markov chain: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
    else:
        # Existing chains found, map them by name
        for chain in chains:
            for key, default_chain in DEFAULT_CHAINS.items():
                if chain.name == default_chain["name"]:
                    default_chain_ids[key] = chain.id
                    logger.info(f"Found existing {key} chain with ID: {chain.id}")
    
    return default_chain_ids


def get_default_chain_ids() -> Dict[str, UUID]:
    """
    Get the IDs of all default chains.
    
    Returns:
        Dictionary mapping chain keys to their UUIDs
    """
    return default_chain_ids 