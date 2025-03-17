import React, { useState } from 'react';
import {
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Button,
  Badge,
  Text,
  Box,
  HStack,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  VStack,
  Heading,
  Alert,
  AlertIcon,
  Flex
} from '@chakra-ui/react';

/**
 * Table component for displaying and managing provider registration requests
 */
const ProviderRequestsTable = ({ providerRequests, onApprove }) => {
  const [selectedProvider, setSelectedProvider] = useState(null);
  const { isOpen, onOpen, onClose } = useDisclosure();

  // Handle view details
  const handleViewDetails = (provider) => {
    setSelectedProvider(provider);
    onOpen();
  };

  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'yellow';
      case 'approved':
        return 'green';
      case 'rejected':
        return 'red';
      default:
        return 'gray';
    }
  };

  // Format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  return (
    <>
      {providerRequests.length === 0 ? (
        <Alert status="info">
          <AlertIcon />
          No provider registration requests found
        </Alert>
      ) : (
        <Box overflowX="auto">
          <Table variant="simple" size="md">
            <Thead>
              <Tr bg="gray.50">
                <Th>Provider Name</Th>
                <Th>Type</Th>
                <Th>Submitted At</Th>
                <Th>Status</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {providerRequests.map((provider) => (
                <Tr key={provider.id} _hover={{ bg: 'gray.50' }}>
                  <Td fontWeight="medium">{provider.name}</Td>
                  <Td>
                    <Badge>
                      {provider.type.charAt(0).toUpperCase() + provider.type.slice(1)}
                    </Badge>
                  </Td>
                  <Td>{formatDate(provider.submitted_at)}</Td>
                  <Td>
                    <Badge colorScheme={getStatusColor(provider.status)}>
                      {provider.status.toUpperCase()}
                    </Badge>
                  </Td>
                  <Td>
                    <HStack spacing={2}>
                      <Button
                        size="sm"
                        colorScheme="blue"
                        variant="outline"
                        onClick={() => handleViewDetails(provider)}
                      >
                        View Details
                      </Button>
                      {provider.status === 'pending' && (
                        <Button
                          size="sm"
                          colorScheme="green"
                          onClick={() => onApprove(provider.id)}
                        >
                          Approve
                        </Button>
                      )}
                    </HStack>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Box>
      )}

      {/* Provider Details Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader borderBottomWidth="1px">
            Provider Registration Details
          </ModalHeader>
          <ModalCloseButton />
          
          <ModalBody py={6}>
            {selectedProvider && (
              <VStack spacing={5} align="stretch">
                <Flex justify="space-between" align="center">
                  <Heading as="h3" size="md">{selectedProvider.name}</Heading>
                  <Badge colorScheme={getStatusColor(selectedProvider.status)} fontSize="md" px={2} py={1}>
                    {selectedProvider.status.toUpperCase()}
                  </Badge>
                </Flex>
                
                <Box p={4} bg="gray.50" borderRadius="md">
                  <Text fontWeight="bold" mb={1}>Provider Type:</Text>
                  <Text>{selectedProvider.type.charAt(0).toUpperCase() + selectedProvider.type.slice(1)}</Text>
                  
                  {selectedProvider.description && (
                    <>
                      <Text fontWeight="bold" mt={3} mb={1}>Description:</Text>
                      <Text>{selectedProvider.description}</Text>
                    </>
                  )}
                  
                  {selectedProvider.website && (
                    <>
                      <Text fontWeight="bold" mt={3} mb={1}>Website:</Text>
                      <Text color="blue.500">
                        <a href={selectedProvider.website} target="_blank" rel="noopener noreferrer">
                          {selectedProvider.website}
                        </a>
                      </Text>
                    </>
                  )}
                </Box>
                
                <Box p={4} bg="blue.50" borderRadius="md">
                  <Heading as="h4" size="sm" mb={3}>Contact Information</Heading>
                  <Text>
                    <strong>Name:</strong> {selectedProvider.contact.name}
                  </Text>
                  {selectedProvider.contact.title && (
                    <Text>
                      <strong>Title:</strong> {selectedProvider.contact.title}
                    </Text>
                  )}
                  <Text>
                    <strong>Email:</strong> {selectedProvider.contact.email}
                  </Text>
                  {selectedProvider.contact.phone && (
                    <Text>
                      <strong>Phone:</strong> {selectedProvider.contact.phone}
                    </Text>
                  )}
                </Box>
                
                {selectedProvider.integration_info && Object.keys(selectedProvider.integration_info).length > 0 && (
                  <Box p={4} bg="green.50" borderRadius="md">
                    <Heading as="h4" size="sm" mb={3}>Integration Information</Heading>
                    {selectedProvider.integration_info.api_documentation && (
                      <Text>
                        <strong>API Documentation:</strong>{' '}
                        <a href={selectedProvider.integration_info.api_documentation} target="_blank" rel="noopener noreferrer">
                          {selectedProvider.integration_info.api_documentation}
                        </a>
                      </Text>
                    )}
                    <Text>
                      <strong>Requires OAuth:</strong> {selectedProvider.integration_info.requires_oauth ? 'Yes' : 'No'}
                    </Text>
                    <Text>
                      <strong>Supports FHIR:</strong> {selectedProvider.integration_info.supports_fhir ? 'Yes' : 'No'}
                    </Text>
                  </Box>
                )}
                
                {selectedProvider.notes && (
                  <Box p={4} borderRadius="md" borderWidth="1px">
                    <Heading as="h4" size="sm" mb={2}>Additional Notes</Heading>
                    <Text>{selectedProvider.notes}</Text>
                  </Box>
                )}
                
                <Box p={4} bg="gray.100" borderRadius="md">
                  <Text fontSize="sm" color="gray.600">
                    <strong>Submitted by:</strong> {selectedProvider.submitted_by}
                  </Text>
                  <Text fontSize="sm" color="gray.600">
                    <strong>Submitted at:</strong> {formatDate(selectedProvider.submitted_at)}
                  </Text>
                </Box>
              </VStack>
            )}
          </ModalBody>

          <ModalFooter borderTopWidth="1px">
            <Button variant="ghost" mr={3} onClick={onClose}>
              Close
            </Button>
            {selectedProvider && selectedProvider.status === 'pending' && (
              <Button 
                colorScheme="green"
                onClick={() => {
                  onApprove(selectedProvider.id);
                  onClose();
                }}
              >
                Approve Provider
              </Button>
            )}
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
};

export default ProviderRequestsTable;
